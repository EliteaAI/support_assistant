from pydantic import BaseModel, Field
from typing import Optional


class ConversationCreateRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
