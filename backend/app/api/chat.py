from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
from app.core.startup import GlobalState
from app.utils.embedder import embed_text
from app.utils.prompt import construct_prompt, generate_system_prompt

router = APIRouter()

class ChatRequest(BaseModel):
    chat_history: List[Dict[str, str]]
    top_k: int = 3

@router.post("/", response_class=StreamingResponse)
def chat(request: ChatRequest):
    try:
        if not request.chat_history:
            raise HTTPException(status_code=400, detail="Chat history cannot be empty")

        latest_user_messages = [msg["content"] for msg in request.chat_history if msg["role"] == "user"]
        if not latest_user_messages:
            raise HTTPException(status_code=400, detail="No user message found in chat history")

        latest_user_message = latest_user_messages[-1]
        intent = GlobalState.intent_detector.detect_intent(latest_user_message)
        query_embedding = embed_text(latest_user_message, GlobalState.embedding_model)
        retrieved_recipes = GlobalState.faiss_handler.search_by_intent(
            query_embedding, intent, top_k=request.top_k
        )

        system_prompt = generate_system_prompt(latest_user_message)
        print(f"System prompt: {system_prompt}")

        prompt = construct_prompt(
            system_prompt=system_prompt,
            retrieved_chunks=retrieved_recipes,
            chat_history=request.chat_history,
            latest_user_message=latest_user_message
        )

        def token_generator():
            for token in GlobalState.llm_runner.stream_response(prompt):
                print(f"Streaming token: {token}", flush=True)
                yield token

        return StreamingResponse(token_generator(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))