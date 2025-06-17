from typing import List, Dict
import re

def construct_prompt(system_prompt: str, retrieved_chunks: list, chat_history: list, latest_user_message: str, llm_runner=None) -> str:
    """
    Constructs a prompt for the LLM with:
    - System prompt
    - Retrieved context
    - Token-truncated chat history (if needed)
    - User's latest input
    Only chat_history is truncated, using model tokenization if llm_runner is provided.
    """
    # Format retrieved context
    if retrieved_chunks:
        context_block = "\n".join(f"Recipe {i+1}:\n{chunk}" for i, chunk in enumerate(retrieved_chunks))
        context_message = f"[Context Retrieved from Knowledge Base]\n{context_block}\n"
    else:
        context_message = "[No context retrieved. Try to respond based on the chat history or ask the user for clarification.]\n"

    # Build full chat history as string
    formatted_history_lines = [f"{msg['role'].capitalize()}: {msg['content']}" for msg in chat_history]
    full_chat_history = "\n".join(formatted_history_lines)

    # Token-aware truncation of chat history
    truncated_chat_history = full_chat_history
    max_chat_tokens = 1500

    if llm_runner:
        chat_tokens = llm_runner.model.tokenize(full_chat_history.encode("utf-8"))
        if len(chat_tokens) > max_chat_tokens:
            print("[DEBUG] Truncating chat history based on token limit...")
            truncated_tokens = chat_tokens[-max_chat_tokens:]
            truncated_chat_history = llm_runner.model.detokenize(truncated_tokens).decode("utf-8", errors="ignore")
            truncated_chat_history = "[Note: Some earlier conversation history was omitted.]\n" + truncated_chat_history

    # Final full prompt assembly
    prompt = (
        f"{system_prompt}\n"
        f"{context_message}"
        f"[Conversation History]\n"
        f"{truncated_chat_history}\n"
        f"The user asked: {latest_user_message}\n"
        f"Assiatnce: You are the assistant. Please respond accordingly."
    )

    return prompt

def generate_system_prompt(user_message: str) -> str:
    INTENT_PATTERNS = {
        "SuggestRecipe": [
            r"\b(suggest|recommend|idea|give me|show|find|any)\b.*\b(recipes?|dishes?|meals?)\b",
            r"\b(what can i make|cook|prepare)\b.*\b(with|using)\b.*",
            r"\b(available ingredients?|leftovers?|at home)\b",
            r"\b(good|easy|quick|simple|healthy).*\brecipes?\b",
            r"\b(dinner|lunch|breakfast|snack).*ideas?\b",
        ],
        "IngredientQuery": [
            r"\b(ingredients?|need(ed)?|using|require|contain|consist of|with|based on|that use|made with|made from|that include|prepare with)\b",
            r"\b(do i need|what do i need|is it made of)\b.*",
        ],
        "InstructionsOnly": [
            r"\b(how to|steps to|prepare|make|cook|method|instruction(s)?)\b.*",
            r"\bprocedure\b",
        ],
        "NutritionInfo": [
            r"\b(calories|nutritional|health(y)?|macro|carbs|protein)\b",
        ],
        "CookingTimeFilter": [
            r"\b(time|required|cook(ing)? time|under \d{1,3} (mins?|minutes?))\b",
            r"\bquick|fast|30 min\b",
        ],
        "DietaryPreferences": [
            r"\b(vegetarian|vegan|gluten[- ]?free|dairy[- ]?free|low carb|low fat|keto|paleo)\b",
        ],
        "ExpandRecipe": [
            r"\b(more details|elaborate|explain more|show full|tell me more)\b",
        ],
        "ToolOrMethodQuery": [
            r"\b(do i need|how to use|can i use|tool(s)?|equipment|machine|oven|grill|stove|microwave)\b",
        ],
    }

    intent_addons = {
        "SuggestRecipe": """
When suggesting recipes:
- Provide **2 to 3 recipes** in valid Markdown format.
- Do not invent or create any values. If any value is not available, skip this line (especially image URLs)
- Strictly **Do not** include or reference instructions, steps, directions, or preparation methods.
- For each recipe, include **exactly and only** the following in **this order**, with **each on its own line** and using the format `Label: Value` (labels must be present):
  Recipe #N: [Recipe Name]
  - ![Image](image URL) (If a valid image URL is available in the data , else skip the image line entirely.)
  - Category: [Category]
  - Calories: [e.g., 312.5]
  - Cook Time: [e.g., "1 hour 30 minutes", not 01:30]
  - Rating: [from 0.0 to 5.0]
  - **Ingredients:** Use a brief Comma-separated list
""",
        "IngredientQuery": """
For ingredient questions:
- Use bullet points with quantities.
- Only suggest recipes that use the ingredients provided or are relevant to what the user has on hand.
""",
        "InstructionsOnly": """
When explaining instructions steps:
- Use a numbered list.
- Avoid adding unrelated commentary.
""",
        "NutritionInfo": """
For nutrition questions:
- Mention calories, macros, and diet types (if known).
- Use a clean, bullet-style summary.
""",
        "CookingTimeFilter": """
For time-based requests:
- Suggest recipes with matching or under X cook time.
- Clearly show total cooking time (e.g., "1 hour 30 minutes", not 01:30).
""",
        "DietaryPreferences": """
Respect dietary preferences like vegan, gluten-free, etc.
- Do not suggest recipes with restricted ingredients.
""",
        "ExpandRecipe": """
If elaborating on a recipe:
- Include full details (name, image, ingredients, instructions, calories, rating, total time).
- Numbered steps for instructions.
""",
        "ToolOrMethodQuery": """
For tool/method questions:
- Briefly explain tool usage.
- Offer alternatives if applicable.
"""
    }

    base_prompt = """
You are a helpful, friendly AI cooking assistant. Always:
- Format responses using proper Markdown syntax (e.g., use **bold** for key terms).
- Ask clarifying questions if the user's request is unclear or ambiguous.
- Do not mention or imply anything about using a "knowledge base", "retrieved context", or similar systems. Avoid all such language.
- Never return a response that is blank, contains only line breaks (e.g., \\n, \\n\\n), or consists solely of whitespace or formatting. This includes cases where no relevant data is found.
- If no suitable data is available or the user's request cannot be confidently answered:
  - You **must** return the following fallback message, formatted in Markdown:
    > _Sorry, I couldn’t find enough relevant information to answer that. Could you please clarify or try rephrasing?_
  - Do **not** return just a blank response or line breaks under any circumstances.
- If context is unclear (e.g., the user says "the second one"), you may use recent chat history to resolve references. If the intent still can't be determined, return the fallback message above.
Always ensure your response is complete, meaningful, and well-structured.
Keep responses concise, warm, and helpful.
"""

    # Normalize input
    user_message = user_message.lower()

    # Detecting intents
    matched_intents = []
    for intent, patterns in INTENT_PATTERNS.items():
        if any(re.search(pattern, user_message) for pattern in patterns):
            matched_intents.append(intent)

    # Building final prompt
    full_prompt = base_prompt
    for intent in matched_intents:
        full_prompt += intent_addons.get(intent, "")

    return full_prompt.strip()