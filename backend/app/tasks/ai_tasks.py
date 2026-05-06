import asyncio
import json
from typing import Any, Dict, List
from uuid import UUID

from app.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.logging_config import get_logger
from app.models import Chats
from app.services.builder_service import BuilderService
from app.services.database_service import ChatService
from app.utils.parse_utils import AIParser


logger = get_logger(__name__)


def _run_async(coro):
    """Helper to run async code in Celery task"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


@celery_app.task(
    name="app.tasks.ai_tasks.generate_ai_build_task",
    bind=True,
    max_retries=3,
)
def generate_ai_build_task(
    self,
    build_id: int,
    user_id: int,
    budget: int,
    goal: str,
    candidates: Dict[str, List[Dict[str, Any]]],
    selected_components: Dict[str, int] | None = None,
) -> Dict[str, Any]:
    """
    Celery task to generate AI build asynchronously.

    Args:
        build_id: ID of the build to update
        user_id: ID of the user who owns the build
        budget: Build budget
        goal: Build goal (esports/aaa/balanced/office)
        candidates: Available components by category
        selected_components: Pre-selected components

    Returns:
        Dict with build components and summary
    """
    async def _generate():
        db = AsyncSessionLocal()
        try:
            # Verify build ownership
            build = await BuilderService.get_build_static(db, build_id)
            if not build or build.user_id != user_id:
                raise PermissionError("Build not found or unauthorized")

            # Prepare AI context
            ai_context = {
                "user_config": {"budget": budget, "goal": goal},
                "candidates": candidates,
                "selected_components": selected_components or {},
            }

            # Call AI parser
            parser = AIParser(source="builder")
            ai_response = parser.call_ai(json.dumps(ai_context))

            if not isinstance(ai_response, dict) or "build" not in ai_response:
                raise ValueError("Invalid AI response format")

            build_components = ai_response.get("build", {})
            summary = ai_response.get("summary", "Build generated successfully")

            # Apply components to the build
            service = BuilderService(db)
            for category, product_id in build_components.items():
                if product_id and isinstance(product_id, int):
                    try:
                        await service.add_or_replace_component(
                            build_id, user_id, category, product_id
                        )
                    except Exception as e:
                        logger.warning(f"Failed to add {category}: {e}")

            return {
                "build": build_components,
                "summary": summary,
                "status": "completed",
            }
        except Exception as e:
            logger.error(f"AI build generation failed: {e}")
            raise
        finally:
            await db.close()

    try:
        return _run_async(_generate())
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise exc


@celery_app.task(
    name="app.tasks.ai_tasks.process_ai_chat_message_task",
    bind=True,
    max_retries=3,
)
def process_ai_chat_message_task(
    self,
    chat_id: str,
    user_id: int,
    message: str,
    prompt_source: str = "chat",
) -> Dict[str, Any]:
    """
    Celery task to process AI chat message asynchronously.

    Args:
        chat_id: UUID of the chat session
        user_id: ID of the user
        message: User's message
        prompt_source: Source of the prompt (chat or builder)

    Returns:
        Dict with AI response
    """
    async def _process():
        db = AsyncSessionLocal()
        try:
            # Convert string to UUID
            chat_uuid = UUID(chat_id)

            # Get chat and verify ownership
            chat = await db.get(Chats, chat_uuid)
            if not chat or chat.user_id != user_id:
                raise PermissionError("Chat not found or unauthorized")

            # Get chat history
            context_history = await ChatService.get_chat_messages(db, user_id, chat_id)

            # Get the build and its components for context
            build = await BuilderService.get_build_static(db, chat.result_id)
            if not build:
                raise ValueError("Build not found")

            # Format build data for AI context
            build_context = {
                "user_config": {
                    "budget": build.budget,
                    "goal": build.goal.value if build.goal else "balanced",
                },
                "selected_components": {
                    bc.category.value: {
                        "id": bc.product_id,
                        "name": bc.product.name,
                        "price": bc.product.price,
                        "specs": bc.product.specs or {},
                    }
                    for bc in build.components
                },
            }

            # Call AI parser
            parser = AIParser(source=prompt_source)
            final_prompt = json.dumps({
                "current_build": build_context,
                "question": message,
            })

            ai_response = parser.call_ai(final_prompt, history=context_history)

            # Parse response
            if isinstance(ai_response, dict):
                answer = ai_response.get('answer') or ai_response.get('text') or 'Unable to process your question'
                explanation = ai_response.get('explanation')
                score = ai_response.get('score') if isinstance(ai_response.get('score'), int) else None
                confidence = ai_response.get('confidence') if isinstance(ai_response.get('confidence'), int) else None
            else:
                answer = str(ai_response)
                explanation = None
                score = None
                confidence = None

            # Save user message
            await ChatService.create_message(
                db,
                chat_uuid,
                message,
                role="user",
                active_indices=chat.active_indices or [],
            )

            # Save assistant message
            await ChatService.create_message(
                db,
                chat_uuid,
                answer,
                role="assistant",
                active_indices=chat.active_indices or [],
            )

            return {
                "answer": answer,
                "explanation": explanation,
                "score": score,
                "confidence": confidence,
                "status": "completed",
            }
        except Exception as e:
            logger.error(f"AI chat processing failed: {e}")
            raise
        finally:
            await db.close()

    try:
        return _run_async(_process())
    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise exc
