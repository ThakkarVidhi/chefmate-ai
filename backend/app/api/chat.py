from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    
class ChatResponse(BaseModel):
    response: str
    
@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    return ChatResponse(response=f"You said: {query}. Recipe details coming soon!")