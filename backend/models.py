from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List

from pydantic import BaseModel, Field


def _generate_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class InboxItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    type: str
    created_at: str = Field(default_factory=_generate_timestamp)


class ChatSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    created_at: str = Field(default_factory=_generate_timestamp)
    updated_at: str = Field(default_factory=_generate_timestamp)


class ChatMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str
    content: str


class ChatInput(BaseModel):
    content: str
    mode: str
    session_id: str | None = None


class DevProject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    status: str = "Capturada"
    progress: int = 0
    tech_stack: List[str] = Field(default_factory=list)
    workspace_path: str
    created_at: str = Field(default_factory=_generate_timestamp)
    main_session_id: str | None = None


class SystemLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str
    type: str
    title: str
    description: str
    agent: str
    project_id: str | None = None


class GeneralSettings(BaseModel):
    language: str = "pt-BR"
    theme: str = "dark"
    auto_save: bool = True


class AIProvider(BaseModel):
    enabled: bool = False
    api_key: str | None = None
    model_name: str | None = None


class OperationMode(str, Enum):
    TURBO = "turbo"
    BALANCED = "balanced"
    ECONOMIC = "economic"
    OFFLINE = "offline"


class AISettings(BaseModel):
    mode: OperationMode = OperationMode.BALANCED
    openai: AIProvider = AIProvider(model_name="gpt-4-turbo")
    google: AIProvider = AIProvider(model_name="gemini-1.5-pro")
    deepseek: AIProvider = AIProvider(enabled=True, model_name="deepseek-chat")
    perplexity: AIProvider = AIProvider(model_name="sonar-medium-online")
    ollama_model: str = "llama3"
    fallback_enabled: bool = True


class SystemSettings(BaseModel):
    general: GeneralSettings = GeneralSettings()
    ai: AISettings = AISettings()
