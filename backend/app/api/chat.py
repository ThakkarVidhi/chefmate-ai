from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import pandas as pd
from typing import List, Literal, Dict
from app.utils.faiss_handler import FAISSHandler
from app.utils.embedder import load_embedding_model, embed_text
from app.utils.helper import load_dataframe
from app.utils.llm_model import LLMRunner
from app.utils.prompt import construct_prompt
from app.utils.config_loader import load_config

router = APIRouter()
config = load_config()
embedding_model = load_embedding_model(config)
df = load_dataframe(config["paths"]["cleaned_data_pkl"])
faiss_handler = FAISSHandler(config, df)
llm_runner = LLMRunner()

class ChatRequest(BaseModel):
    chat_history: List[Dict[str, str]]
    top_k: int = 3
    
class ChatResponse(BaseModel):
    response: object

@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if not request.chat_history:
            raise HTTPException(status_code=400, detail="Chat history cannot be empty")

        # Extract the latest user message from the chat history
        print("Chat history:", request.chat_history)
        latest_user_messages = [msg["content"] for msg in request.chat_history if msg["role"] == "user"]
        if not latest_user_messages:
            raise HTTPException(status_code=400, detail="No user message found in chat history")
        
        latest_user_message = latest_user_messages[-1]

        # Embed the latest user query for retrieval
        query_embedding = embed_text(latest_user_message, embedding_model)
        print("Query embedding:", query_embedding)

        # Inside your chat route
        retrieved_recipes = faiss_handler.search(query_embedding, top_k=3)
        print("Retrieved recipes:", retrieved_recipes)
        
        system_prompt = "You are a helpful AI cooking assistant. Always answer in a warm, friendly tone with step-by-step guidance. If you don't know the answer, say 'I don't know'. If you need more information, ask the user for clarification."

        prompt = construct_prompt(
            system_prompt=system_prompt,
            retrieved_chunks=retrieved_recipes,
            chat_history=request.chat_history,
            latest_user_message=latest_user_message
        )

        print("Constructed prompt:", prompt)
        
        llm_output = llm_runner.generate_response(prompt)
        print("LLM output:", llm_output)

        return ChatResponse(response=llm_output)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))