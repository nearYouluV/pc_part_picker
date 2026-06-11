from fastapi import APIRouter, Depends, HTTPException, status

from app.celery_app import celery_app
from app.models.user import User
from app.scraping_schemas import ScrapingTaskStatusResponse, ScrapingTriggerRequest, ScrapingTriggerResponse
from app.services.auth_service import get_current_admin_user
from app.tasks.scraping_tasks import SUPPORTED_TRIGGER_CATEGORIES, scrape_category_task


router = APIRouter(prefix="/scraping", tags=["scraping"])


@router.post("/trigger", response_model=ScrapingTriggerResponse)
async def trigger_scraping(
    payload: ScrapingTriggerRequest,
    current_user: User = Depends(get_current_admin_user),
):
    category = payload.category.strip().lower()
    if category not in SUPPORTED_TRIGGER_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported category. Allowed: {', '.join(sorted(SUPPORTED_TRIGGER_CATEGORIES.keys()))}",
        )

    task = scrape_category_task.delay(category)

    return ScrapingTriggerResponse(
        task_id=task.id,
        category=category,
        status="queued",
    )


@router.get("/status/{task_id}", response_model=ScrapingTaskStatusResponse)
async def get_scraping_status(
    task_id: str,
    current_user: User = Depends(get_current_admin_user),
):
    result = celery_app.AsyncResult(task_id)
    if result.state in {"PENDING", "RECEIVED", "STARTED", "RETRY", "QUEUED"}:
        status_value = "processing" if result.state in {"STARTED", "RETRY"} else "queued"
    elif result.state == "SUCCESS":
        status_value = "completed"
    elif result.state == "FAILURE":
        status_value = "failed"
    else:
        status_value = result.state.lower()

    category = None
    if isinstance(result.result, dict):
        category = result.result.get("category")

    return ScrapingTaskStatusResponse(task_id=task_id, status=status_value, category=category)
