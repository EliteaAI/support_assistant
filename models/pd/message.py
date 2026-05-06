from pydantic import BaseModel, Field
from typing import Optional, List


class MessageCreateRequest(BaseModel):
    content: str = Field(..., min_length=1)
    attachments: Optional[List[str]] = None
