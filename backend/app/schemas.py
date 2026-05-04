from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class ChatCreateRequest(BaseModel):
    result_id: Optional[int] = None


class ChatRequest(BaseModel):
    chat_id: UUID
    message: str
    prompt_source: Optional[str] = "chat"


class ChatResponse(BaseModel):
    answer: str
    explanation: Optional[str] = None
    score: Optional[int] = None
    confidence: Optional[int] = None


class IndexSelectRequest(BaseModel):
    chat_id: UUID
    index_name: str


class PromptSelectRequest(BaseModel):
    chat_id: UUID
    prompt_source: str


class CreatePromptRequest(BaseModel):
    id: Optional[int] = None
    source: str
    prompt: str
    instructions: str
    temperature: float = Field(0.7, ge=0.0, le=1.0)
    version: int = 1


class PromptResponse(BaseModel):
    id: int
    source: str
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None


class DetailedPromptResponse(BaseModel):
    id: int
    source: str
    prompt: str
    instructions: str
    temperature: float
    version: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
