from pydantic import BaseModel, ConfigDict
from typing import Optional


class ConfigUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    agent_id: Optional[str] = None
    agent_project_id: Optional[int] = None
    welcome_message: Optional[str] = None
    assistant_name: Optional[str] = None
    support_project_id: Optional[int] = None
    placeholder: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "enabled": True,
                    "agent_id": "abc123",
                    "agent_project_id": 42,
                    "welcome_message": "Hello! How can I help you today?",
                    "assistant_name": "ELITEA Support",
                    "support_project_id": 7,
                    "placeholder": "Type a message...",
                }
            ]
        }
    )
