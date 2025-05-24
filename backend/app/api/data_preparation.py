from fastapi import APIRouter, HTTPException
from backend.app.utils.recipe_preprocessor import load_recipe_data, clean_recipe_data
from app.utils.embedder import generate_recipe_embeddings
from app.utils.faiss_handler import build_recipe_faiss_indexes
from app.utils.config_loader import load_config

router = APIRouter()
config = load_config()

@router.post("/initialize-recipes")
def initialize_recipes():
    try:
        df = load_recipe_data(config["paths"]["recipe_data"])
        if df.empty:
            raise HTTPException(status_code=500, detail="Failed to load data.")

        df = clean_recipe_data(df)
        df = generate_recipe_embeddings(df, config)

        df.to_csv(config["paths"]["cleaned_data_csv"], index=False)
        df.to_pickle(config["paths"]["cleaned_data_pkl"])

        build_recipe_faiss_indexes(df, config)

        return {"status": "success", "message": "Data prepared and indexed."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))