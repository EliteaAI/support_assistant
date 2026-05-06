from pydantic import BaseModel, Field
from typing import Optional, List


class SupportPredictPayload(BaseModel):
    conversation_uuid: str
    content: str = Field(..., min_length=1)
    attachments: Optional[List[str]] = None
