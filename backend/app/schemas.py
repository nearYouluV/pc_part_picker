from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatCreateRequest(BaseModel):
    build_id: int


class ChatRequest(BaseModel):
    chat_id: UUID
    message: str
    prompt_source: Optional[str] = "chat"


class ChatResponse(BaseModel):
    answer: str
    explanation: Optional[str] = None
    score: Optional[int] = None
    confidence: Optional[int] = None

class TaskResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ComponentCandidate(BaseModel):
    id: int
    name: str
    price: float
    category: str
    specs: Dict[str, Any]
    score: float


class BuildUserConfig(BaseModel):
    budget: int
    goal: str


class AIBuildRequest(BaseModel):
    build_id: int
    user_config: BuildUserConfig
    candidates: Dict[str, List[ComponentCandidate]]
    selected_components: Optional[Dict[str, int]] = None


class AIBuildResponse(BaseModel):
    build: Dict[str, int]
    summary: str


class AIChatFollowupRequest(BaseModel):
    chat_id: UUID
    current_build: Dict[str, Any]
    candidates: Dict[str, List[ComponentCandidate]]
    question: str
