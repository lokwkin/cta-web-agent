from pydantic import BaseModel
from typing import Optional


class ReActOutput(BaseModel):
    situation: Optional[str]
    options: Optional[str]
    thought: Optional[str]
    action: str
    action_params: Optional[dict]
    action_desc: Optional[str]
