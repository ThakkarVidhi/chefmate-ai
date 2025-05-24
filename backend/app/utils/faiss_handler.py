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
        self.df = df.set_index("faiss_index")
        self.index_dir = config["paths"]["faiss_index_dir"]

        self.embedding_columns = {
            "ingredients_cleaned": "ingredients_embedding",
            "ingredients_with_quantities": "ingredients_with_quantities_embedding",
            "name": "title_embedding"
        }

        self.indexes = {}
        self.load_indexes()

        self.result_columns = [
            "name", "ingredients_cleaned", "ingredients_with_quantities",
            "recipe_instructions", "recipe_category", "calories",
            "total_time", "aggregated_rating", "recipe_yield", "images"
        ]
        
    def load_indexes(self):
        for _, embed_col in self.embedding_columns.items():
            index_path = os.path.join(self.index_dir, f"{embed_col}.index")
            if not os.path.exists(index_path):
                raise FileNotFoundError(f"Index not found at {index_path}")
            self.indexes[embed_col] = faiss.read_index(index_path)

    def _get_metadata_by_index(self, idx: int, minimal: bool = False):
        """Returns recipe data by FAISS index with optional minimal output."""
        if idx not in self.df.index:
            return None

        row = self.df.loc[idx]
        if minimal:
            return {
                "faiss_index": idx,
                "name": row["name"],
                "ingredients_with_quantities": row["ingredients_with_quantities"],
                "recipe_instructions": row.get("recipe_instructions", ""),
                "category": row.get("recipe_category", ""),
                "calories": row.get("calories", ""),
                "total_time": row.get("total_time", ""),
                "rating": row.get("aggregated_rating", None),
                "images": row.get("images", [])
            }
        else:
            # Return full recipe without embedding columns
            full_row = row.drop(list(self.embedding_columns.values()), errors='ignore')
            return {"faiss_index": idx, **full_row.to_dict()}

    def search_by_intent(self, query_embedding: np.ndarray, intent: str, top_k: int = 5):
        query_vector = np.array([query_embedding]).astype("float32")

        if intent == "ingredient_search":
            target_key = "ingredients_cleaned"
        elif intent == "specific_recipe":
            target_key = "name"
        elif intent == "recipe_generation":
            target_key = "ingredients_with_quantities"
        else:
            return self.default_search(query_embedding, top_k)

        embed_col = self.embedding_columns[target_key]
        index = self.indexes.get(embed_col)

        if index is None:
            raise ValueError(f"No index for intent '{intent}'")

        distances, indices = index.search(query_vector, top_k)
        results = []

        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            metadata = self._get_metadata_by_index(idx, minimal=True)
            if metadata:
                results.append((dist, metadata))

        results = sorted(results, key=lambda x: x[0])
        return [r[1] for r in results[:top_k]]

    def default_search(self, query_embedding: np.ndarray, top_k: int = 5):
        query_vector = np.array([query_embedding]).astype("float32")

        all_results = []
        for embed_col, index in self.indexes.items():
            distances, indices = index.search(query_vector, top_k)
            for dist, idx in zip(distances[0], indices[0]):
                if idx == -1:
                    continue
                metadata = self._get_metadata_by_index(idx, minimal=True)
                if metadata:
                    all_results.append((dist, metadata))

        all_results = sorted(all_results, key=lambda x: x[0])
        return [r[1] for r in all_results[:top_k]]

    def get_recipe_by_faiss_index(self, faiss_index: int):
        return self._get_metadata_by_index(faiss_index, minimal=False)
