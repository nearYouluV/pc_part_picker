from fastapi import APIRouter, Depends, HTTPException
from app.schemas import (
    ChatRequest,
    ChatCreateRequest,
    ChatResponse,
    AIBuildRequest,
    AIBuildResponse,
    TaskResponse,
    TaskStatusResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import get_current_active_user
from app.models.user import User
from app.database import get_async_db
from app.models import Chats
from app.services.database_service import ChatService
from app.services.builder_service import BuilderService
from app.tasks.ai_tasks import generate_ai_build_task, process_ai_chat_message_task
from app.celery_app import celery_app

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/build")
async def ai_build(
    data: AIBuildRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
) -> TaskResponse:
    """Dispatch AI build generation task (async via Celery)"""

    # Verify the build belongs to the current user
    build = await BuilderService.get_build_static(db, data.build_id)
    if not build or build.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Build not found")

    # Dispatch Celery task
    task = generate_ai_build_task.delay(
        build_id=data.build_id,
        user_id=current_user.id,
        budget=data.user_config.budget,
        goal=data.user_config.goal,
        candidates={
            category: [c.dict() for c in components]
            for category, components in data.candidates.items()
        },
        selected_components=data.selected_components,
    )

    return TaskResponse(task_id=task.id, status="processing")


@router.post("/chat")
async def create_ai_chat(
    data: ChatCreateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create or get existing chat session for a build"""

    # Verify the build belongs to the current user
    build = await BuilderService.get_build_static(db, data.build_id)
    if not build or build.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Build not found")

    # Use build_id as result_id for compatibility with existing chat model
    chat = await ChatService.get_or_create_chat_for_result(
        db, current_user.id, data.build_id
    )

    return {
        "id": str(chat.id),
        "user_id": chat.user_id,
        "result_id": chat.result_id,
        "created_at": chat.created_at.isoformat(),
        "active_indices": chat.active_indices or []
    }


@router.post("/chat/message")
async def chat_message(
    data: ChatRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
) -> TaskResponse:
    """Dispatch AI chat message processing task (async via Celery)"""

    chat = await db.get(Chats, data.chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Dispatch Celery task
    task = process_ai_chat_message_task.delay(
        chat_id=str(data.chat_id),
        user_id=current_user.id,
        message=data.message,
        prompt_source=data.prompt_source or "chat",
    )

    return TaskResponse(task_id=task.id, status="processing")


@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
) -> TaskStatusResponse:
    """Get status and result of an AI task"""

    task = celery_app.AsyncResult(task_id)

    if task.state == "PENDING":
        return TaskStatusResponse(
            task_id=task_id,
            status="pending",
        )
    elif task.state == "PROGRESS":
        return TaskStatusResponse(
            task_id=task_id,
            status="processing",
        )
    elif task.state == "SUCCESS":
        return TaskStatusResponse(
            task_id=task_id,
            status="completed",
            result=task.result,
        )
    elif task.state == "FAILURE":
        return TaskStatusResponse(
            task_id=task_id,
            status="failed",
            error=str(task.info),
        )
    elif task.state == "RETRY":
        return TaskStatusResponse(
            task_id=task_id,
            status="retrying",
        )
    else:
        return TaskStatusResponse(
            task_id=task_id,
            status=task.state.lower(),
        )


@router.get("/chat/history/{chat_id}")
async def get_chat_history(
    chat_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get chat history for a specific chat session"""
    return await ChatService.get_chat_messages(db, current_user.id, chat_id)
