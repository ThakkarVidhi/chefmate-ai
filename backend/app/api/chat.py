from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import pandas as pd
from typing import List, Dict
from app.utils.faiss_handler import FAISSHandler
from app.utils.llm_model import LLMRunner
from app.utils.intent_detector import IntentDetector
from app.utils.embedder import load_embedding_model, embed_text
from app.utils.helper import load_dataframe
from app.utils.prompt import construct_prompt, generate_system_prompt
from app.utils.config_loader import load_config

router = APIRouter()
config = load_config()
embedding_model = load_embedding_model(config)
df = load_dataframe(config["paths"]["cleaned_data_pkl"])
faiss_handler = FAISSHandler(config, df)
intent_detector = IntentDetector()
llm_runner = LLMRunner()

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

        intent = intent_detector.detect_intent(latest_user_message)
        query_embedding = embed_text(latest_user_message, embedding_model)
        retrieved_recipes = faiss_handler.search_by_intent(query_embedding, intent, top_k=request.top_k)

        system_prompt = generate_system_prompt(latest_user_message)
        print(f"System prompt: {system_prompt}")

        prompt = construct_prompt(
            system_prompt=system_prompt,
            retrieved_chunks=retrieved_recipes,
            chat_history=request.chat_history,
            latest_user_message=latest_user_message
        )

        def token_generator():
            for token in llm_runner.stream_response(prompt):
                print(f"Streaming token: {token}", flush=True)
                yield token

        return StreamingResponse(token_generator(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))