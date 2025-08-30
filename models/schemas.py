# from pydantic import BaseModel
# from typing import List, Literal

# class ChatMessage(BaseModel):
#     role: Literal['user', 'assistant']
#     content: str

# class ChatRequest(BaseModel):
#     session_id: str
#     voice_id: str
#     audio: bytes

# class ChatResponse(BaseModel):
#     transcript: str
#     reply: str
#     audio_url: str




from pydantic import BaseModel
from typing import Optional


class WSMessage(BaseModel):
    """Generic WebSocket message schema (optional, for future use)."""
    type: str
    data: Optional[str] = None
    text: Optional[str] = None


class GeminiResponse(BaseModel):
    type: str = "gemini_response"
    text: str


class MurfAudioChunk(BaseModel):
    type: str = "murf_audio"
    audio: str  # base64


