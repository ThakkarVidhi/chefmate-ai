from fastapi import FastAPI
from app.api.chat import router as chat_router

app = FastAPI(title="AI Cooking Assistant")

app.include_router(chat_router, prefix="/chat")

@app.get("/")
def root():
    return {"message": "Welcome to the AI Cooking Assistant API!"}