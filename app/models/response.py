from typing import Any, Optional
from pydantic import BaseModel

class APIResponse(BaseModel):
    message: str
    code: str
    value: Optional[Any] = None 