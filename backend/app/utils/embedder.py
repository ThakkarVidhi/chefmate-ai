from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm

def generate_recipe_embeddings(df, config):
    model_name = config["embedding"]["model_name"]
    batch_size = config["embedding"]["batch_size"]

    embedding_model = SentenceTransformer(model_name)
    columns_to_embed = {
        "ingredients_cleaned": "ingredients_embedding",
        "ingredients_with_quantities": "ingredients_with_quantities_embedding",
        "name": "title_embedding"
    }

    for text_col, embed_col in columns_to_embed.items():
        print(f"Embedding column: {text_col}")
        texts = df[text_col].fillna("").astype(str).tolist()

        embeddings = []
        for i in tqdm(range(0, len(texts), batch_size)):
            batch = texts[i:i + batch_size]
            batch_embeddings = embedding_model.encode(batch, show_progress_bar=False)
            embeddings.extend(batch_embeddings)

        df[embed_col] = [emb.tolist() for emb in embeddings]

    return df