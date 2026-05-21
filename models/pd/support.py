from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class SupportAssistantContext(BaseModel):
    assistant_name: Optional[str] = None
    assistant_version: Optional[str] = None
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    current_page: Optional[str] = None
    current_entity_type: Optional[str] = None
    current_entity_id: Optional[int] = None
    current_entity_name: Optional[str] = None
    selected_provider: Optional[str] = None
    selected_model: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class SupportPredictPayload(BaseModel):
    conversation_uuid: str
    content: str = Field(..., min_length=1)
    attachments: Optional[List[str]] = None
    support_assistant_context: Optional[SupportAssistantContext] = None
    question_id: Optional[int] = None
