from typing import List, Dict

def construct_prompt(system_prompt: str, retrieved_chunks: list, chat_history: list, latest_user_message: str) -> str:
    """
    Constructs a complete prompt for the language model by combining:
    - a system prompt
    - context retrieved from vector DB
    - chat history
    - latest user query
    """
    # Format retrieved chunks
    context_block = "\n".join(f"Recipe {i+1}:\n{chunk}" for i, chunk in enumerate(retrieved_chunks))

    # Format chat history
    formatted_history = ""
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]
        formatted_history += f"{role.capitalize()}: {content}\n"

    # Combine all parts
    prompt = (
        f"{system_prompt}\n"
        f"[Context Retrieved from Knowledge Base]\n"
        f"{context_block}\n"
        f"[Conversation History]\n"
        f"{formatted_history}\n"
        f"The user asked: {latest_user_message}\n"
        f"Assiatnce: You are the assistant. Please respond accordingly."
    )
    return prompt