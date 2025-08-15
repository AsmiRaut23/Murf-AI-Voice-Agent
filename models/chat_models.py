from pydantic import BaseModel
from typing import List, Literal

class ChatMessage(BaseModel):
    role: Literal['user', 'assistant']
    content: str

class ChatRequest(BaseModel):
    session_id: str
    voice_id: str
    audio: bytes

class ChatResponse(BaseModel):
    transcript: str
    reply: str
    audio_url: str

