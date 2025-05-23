from app.utils.config_loader import load_config
from app.utils.embedder import load_embedding_model
from app.utils.helper import load_dataframe
from app.utils.faiss_handler import FAISSHandler
from app.utils.intent_detector import IntentDetector
from app.utils.llm_model import LLMRunner

class GlobalState:
    config = None
    embedding_model = None
    df = None
    faiss_handler = None
    intent_detector = None
    llm_runner = None

def init_dependencies():
    if GlobalState.config is None:
        GlobalState.config = load_config()
        print(f"Loaded config: {GlobalState.config}")

    if GlobalState.embedding_model is None:
        GlobalState.embedding_model = load_embedding_model(GlobalState.config)
        print(f"Loaded embedding model: {GlobalState.embedding_model}")

    if GlobalState.df is None:
        GlobalState.df = load_dataframe(GlobalState.config["paths"]["cleaned_data_pkl"])
        print(f"Loaded dataframe: {GlobalState.df.columns}")

    if GlobalState.faiss_handler is None:
        GlobalState.faiss_handler = FAISSHandler(GlobalState.config, GlobalState.df)
        print(f"Initialized FAISS handler with {len(GlobalState.faiss_handler.indexes)} items")

    if GlobalState.intent_detector is None:
        GlobalState.intent_detector = IntentDetector()
        print(f"Initialized intent detector")

    if GlobalState.llm_runner is None:
        GlobalState.llm_runner = LLMRunner()
        print(f"Initialized LLM runner")