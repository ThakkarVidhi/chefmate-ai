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

    if GlobalState.embedding_model is None:
        GlobalState.embedding_model = load_embedding_model(GlobalState.config)

    if GlobalState.df is None:
        GlobalState.df = load_dataframe(GlobalState.config["paths"]["cleaned_data_pkl"])

    if GlobalState.faiss_handler is None:
        GlobalState.faiss_handler = FAISSHandler(GlobalState.config, GlobalState.df)

    if GlobalState.intent_detector is None:
        GlobalState.intent_detector = IntentDetector()

    if GlobalState.llm_runner is None:
        GlobalState.llm_runner = LLMRunner()