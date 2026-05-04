from pydantic import BaseModel


class ScrapingTriggerRequest(BaseModel):
    category: str


class ScrapingTriggerResponse(BaseModel):
    task_id: str
    category: str
    status: str


class ScrapingTaskStatusResponse(BaseModel):
    task_id: str
    status: str
    category: str | None = None
