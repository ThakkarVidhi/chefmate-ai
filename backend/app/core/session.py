from typing import Dict, List, Optional

class SessionMemory:
    def __init__(self):
        self.suggested_recipe_faiss_ids: List[int] = []
        self.active_recipe_index: Optional[int] = None
        self.last_user_query: Optional[str] = None
        self.suggested_recipes: List[Dict] = []
        self.active_recipe: Optional[Dict] = None

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, SessionMemory] = {}

    def get_session(self, session_id: str) -> SessionMemory:
        if session_id not in self.sessions:
            self.sessions[session_id] = SessionMemory()
        return self.sessions[session_id]

    def clear_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]