import os
import numpy as np
import faiss

def build_recipe_faiss_indexes(df, config):
    columns_to_embed = {
        "ingredients_cleaned": "ingredients_embedding",
        "ingredients_with_quantities": "ingredients_with_quantities_embedding",
        "name": "title_embedding"
    }

    index_dir = config["paths"]["faiss_index_dir"]
    os.makedirs(index_dir, exist_ok=True)

    for _, embed_col in columns_to_embed.items():
        print(f"Building FAISS index for: {embed_col}")
        embeddings = np.array(df[embed_col].tolist()).astype('float32')
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)

        index_path = os.path.join(index_dir, f"{embed_col}.index")
        faiss.write_index(index, index_path)
        print(f"Saved FAISS index to: {index_path}")