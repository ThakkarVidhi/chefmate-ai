from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import json

from app.core.startup import GlobalState
from app.utils.embedder import embed_text
from app.utils.prompt import construct_prompt, generate_system_prompt

router = APIRouter()

class ChatRequest(BaseModel):
    chat_history: List[Dict[str, str]]

@router.post("/", response_class=StreamingResponse)
def chat(request: ChatRequest):
    try:
        # Validate chat history
        if not request.chat_history:
            raise HTTPException(status_code=400, detail="Chat history cannot be empty")

        # Extract the most recent user message
        latest_user_messages = [msg["content"] for msg in request.chat_history if msg["role"] == "user"]
        if not latest_user_messages:
            raise HTTPException(status_code=400, detail="No user message found in chat history")

        latest_user_message = latest_user_messages[-1]

        # Detect intent and get embedding
        intent = GlobalState.intent_detector.detect_intent(latest_user_message)
        query_embedding = embed_text(latest_user_message, GlobalState.embedding_model)

        # Retrieve relevant recipes (documents/snippets) using FAISS
        retrieved_recipes = GlobalState.faiss_handler.search_by_intent(
            query_embedding, intent, top_k=3
        )

        # Construct system and user prompts
        system_prompt = generate_system_prompt(latest_user_message)

        prompt = construct_prompt(
            system_prompt=system_prompt,
            retrieved_chunks=retrieved_recipes,
            chat_history=request.chat_history,
            latest_user_message=latest_user_message
        )

        # Stream tokens from LLM
        def token_generator():
            try:
                for token in GlobalState.llm_runner.stream_response(prompt):
                    yield json.dumps({"type": "token", "content": token}) + "\n"
                yield json.dumps({"type": "done"}) + "\n"
            except Exception as e:
                yield json.dumps({"type": "error", "message": str(e)}) + "\n"

        return StreamingResponse(token_generator(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))