from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.config_loader import load_config

router = APIRouter()
config = load_config()

class ChatRequest(BaseModel):
    query: str
    
class ChatResponse(BaseModel):
    response: object

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")

        # 👇 Use pre-built FAISS index, cleaned data, etc. for chat response here
        # response = your_chat_handler(query)
        response = {"message": "Chat logic not yet implemented"}

        return ChatResponse(response=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))