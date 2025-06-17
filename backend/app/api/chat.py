from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict
import json
from app.core.startup import GlobalState
from app.utils.embedder import embed_text
from app.utils.prompt import construct_prompt, generate_system_prompt
from app.utils.helper import interpret_user_selection, convert_numpy, is_requesting_new_suggestions

router = APIRouter()

class ChatRequest(BaseModel):
    session_id: str
    chat_history: List[Dict[str, str]]


@router.post("/", response_class=StreamingResponse)
def chat(request: ChatRequest):
    try:
        session_id = request.session_id
        session = GlobalState.session_manager.get_session(session_id)
        print(f"[DEBUG] Session ID: {session_id}")
        print(f"[DEBUG] Session state: {session}")
        
        # Extract all user messages from chat history
        user_messages = [msg["content"] for msg in request.chat_history if msg["role"] == "user"]

        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found in chat history")

        user_input = user_messages[-1].lower()
        print(f"[DEBUG] User input: {user_input}")

        suggestions = session.suggested_recipes or []
        active_recipe = session.active_recipe
        print(f"[DEBUG] Suggestions available: {len(suggestions)}, Active recipe: {bool(active_recipe)}")

        # Helper functions for recipe retrieval and setting active recipe
        def retrieve_and_set_suggestions(session, user_input: str):
            intent = GlobalState.intent_detector.detect_intent(user_input)
            embedding = embed_text(user_input, GlobalState.embedding_model)
            suggestions = GlobalState.faiss_handler.search_by_intent(embedding, intent, top_k=3)

            session.suggested_recipes = suggestions
            session.suggested_recipe_faiss_ids = [s.get("faiss_index") for s in suggestions]
            session.active_recipe = {}
            session.active_recipe_index = None
            return suggestions

        def set_active_recipe(session, index: int):
            print(session.suggested_recipes, " [DEBUG] Suggested recipes before setting active recipe")
            selected_metadata = session.suggested_recipes[index]
            print(f"[DEBUG] Setting active recipe with index: {index}, metadata: {selected_metadata}")
            faiss_index = selected_metadata.get("faiss_index")
            print(faiss_index, " [DEBUG] Selected FAISS index")
            full_recipe = GlobalState.faiss_handler.get_recipe_by_faiss_index(faiss_index)
            print(f"[DEBUG] Full recipe retrieved: {full_recipe}")

            session.active_recipe = full_recipe
            session.active_recipe_index = faiss_index 
            
            print(f"[DEBUG] Session Index: {session.active_recipe_index}")
            return full_recipe

        # ========================
        # Case 1: No active recipe
        # ========================
        if not active_recipe:
            if not suggestions:
                print("[DEBUG] No suggestions yet. Generating new suggestions...")
                suggestions = retrieve_and_set_suggestions(session, user_input)
            elif is_requesting_new_suggestions(user_input):
                print("[DEBUG] User requested new suggestions. Refreshing...")
                suggestions = retrieve_and_set_suggestions(session, user_input)
            else:
                print("[DEBUG] User did not request new suggestions. Using existing suggestions.")
                index = interpret_user_selection(user_input, suggestions)
                print(f"[DEBUG] Interpreted selection index: {index}")
                if index is not None:
                    active_recipe = set_active_recipe(session, index)
                    print("[DEBUG] Active recipe has been set.")

        # ===========================
        # Case 2: Active recipe exists
        # ===========================
        else:
            if is_requesting_new_suggestions(user_input):
                print("[DEBUG] User asked for new suggestions despite active recipe.")
                suggestions = retrieve_and_set_suggestions(session, user_input)
                session.active_recipe = {}
                active_recipe = {}

        # ===============================
        # Prompt generation for LLM call
        # ===============================
        system_prompt = generate_system_prompt(user_input)
        context_chunks = [session.active_recipe] if session.active_recipe else session.suggested_recipes

        prompt = construct_prompt(
            system_prompt=system_prompt,
            retrieved_chunks=context_chunks,
            chat_history=request.chat_history,
            latest_user_message=user_input,
            llm_runner=GlobalState.llm_runner
        )
        print(f"[DEBUG] Prompt constructed. Sending to LLM...{prompt}")

        # =========================
        # Streaming LLM response
        # =========================
        def token_generator():
            try:
                # Send metadata first
                metadata = convert_numpy({
                    "active_recipe": session.active_recipe,
                    "suggested_recipes": session.suggested_recipes
                })
                yield json.dumps({"event": "metadata", "data": json.dumps(metadata)}) + "\n"

                # Yield tokens from LLM one by one
                for token in GlobalState.llm_runner.stream_response(prompt):
                    print(f"[DEBUG] Yielding token: {token}")
                    yield json.dumps({"event": "token", "data": token}) + "\n"

                yield json.dumps({"event": "done"}) + "\n"

            except Exception as e:
                print(f"[ERROR] Streaming failed: {str(e)}")
                yield json.dumps({"event": "error", "message": str(e)}) + "\n"

        return StreamingResponse(token_generator(), media_type="text/event-stream")

    except Exception as e:
        print(f"[ERROR] Chat endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))