import os
import numpy as np
import faiss
import pickle

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
        
class FAISSHandler:
    def __init__(self, config, df):
        self.config = config
        self.df = df
        self.index_dir = config["paths"]["faiss_index_dir"]
        
        print(self.df.columns.tolist())

        self.embedding_columns = {
            "ingredients_cleaned": "ingredients_embedding",
            "ingredients_with_quantities": "ingredients_with_quantities_embedding",
            "name": "title_embedding"
        }

        self.indexes = {}
        self.load_indexes()

        # Optionally create a metadata store: row_id -> recipe data
        self.metadata_store = {
            idx: {
                "name": row["name"],
                "ingredients": row["ingredients_cleaned"],
                "ingredients_with_quantities": row["ingredients_with_quantities"],
                "recipe_instructions": row.get("recipe_instructions", ""),
                "category": row.get("recipe_category", ""),
                "calories": row.get("calories", ""),
                "total_time": row.get("total_time", ""),
                "rating": row.get("aggregated_rating", None),
                "recipe_yield": row.get("recipe_yield", "")
            }
            for idx, row in df.iterrows()
            
        }
        
        print(f"Metadata store size: {len(self.metadata_store)}")

    def load_indexes(self):
        for _, embed_col in self.embedding_columns.items():
            index_path = os.path.join(self.index_dir, f"{embed_col}.index")
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"Index not found at {index_path}")
            print(f"Loading index for: {embed_col}")
            index = faiss.read_index(index_path)
            self.indexes[embed_col] = index

    def search(self, query_embedding: np.ndarray, top_k=5):
        query_vector = np.array([query_embedding]).astype("float32")

        all_results = []
        for embed_col, index in self.indexes.items():
            distances, indices = index.search(query_vector, top_k)
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue
                metadata = self.metadata_store.get(idx)
                if metadata:
                    all_results.append((dist, metadata))

        # Sort by distance (lower = more similar)
        all_results = sorted(all_results, key=lambda x: x[0])
        top_results = [r[1] for r in all_results[:top_k]]
        return top_results