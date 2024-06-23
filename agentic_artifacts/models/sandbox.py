from pydantic import BaseModel
from typing import Optional

class Sandbox(BaseModel):
    id: str
    code: str
    environment: str
    status: str
    error: Optional[str] = None
    preview_url: Optional[str] = None

class SandboxCreate(BaseModel):
    code: str
    environment: str