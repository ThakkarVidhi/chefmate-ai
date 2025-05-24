from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.startup import init_dependencies
from app.api.data_preparation import router as data_router 
from app.api.chat import router as chat_router

origins = [
    "http://localhost:3000",        
    "http://127.0.0.1:3000"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_dependencies()
    yield

app = FastAPI(title="Chefmate AI", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/chat")
app.include_router(data_router, prefix="/data")

@app.get("/")
def root():
    return {"message": "Welcome to the Chefmate AI API!"}