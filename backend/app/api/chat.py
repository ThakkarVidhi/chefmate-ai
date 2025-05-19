from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.preprocess import load_recipe_data, clean_recipe_data
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
        
        recipe_data_path = config["paths"]["recipe_data"]
        df = load_recipe_data(recipe_data_path)
        print(f"Loaded recipe data: {df.head()}")
        clean_df = clean_recipe_data(df)

        
        return ChatResponse(response={clean_df.head().to_json()})
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))