from typing import List, Dict
import re

def construct_prompt(system_prompt: str, retrieved_chunks: list, chat_history: list, latest_user_message: str) -> str:
    """
    Constructs a complete prompt for the language model by combining:
    - a system prompt
    - context retrieved from vector DB
    - chat history
    - latest user query
    """
    # Formatting retrieved chunks
    context_block = "\n".join(f"Recipe {i+1}:\n{chunk}" for i, chunk in enumerate(retrieved_chunks))

    # Formatting chat history
    formatted_history = ""
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]
        formatted_history += f"{role.capitalize()}: {content}\n"

    # Combining all parts
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
            r"\b(ingredients?|need(ed)?|require|contain|consist of)\b",
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
- Provide 2–3 options.
- Include name, category, calories, cook time, and rating.
- Add image (Markdown) if available.
- Brief list of ingredients.
""",
        "IngredientQuery": """
For ingredient questions:
- Use bullet points with quantities.
- Only include relevant ingredients.
""",
        "InstructionsOnly": """
When explaining steps:
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
- Clearly show total cooking time.
""",
        "DietaryPreferences": """
Respect dietary preferences like vegan, gluten-free, etc.
- Do not suggest recipes with restricted ingredients.
""",
        "ExpandRecipe": """
If elaborating on a recipe:
- Include full details (name, ingredients, instructions, image, calories, rating, total time).
""",
        "ToolOrMethodQuery": """
For tool/method questions:
- Briefly explain tool usage.
- Offer alternatives if applicable.
"""
    }

    base_prompt = """
You are a helpful, friendly AI cooking assistant. Always:
- Format responses using Markdown.
- Use **bold** for key terms.
- Bullet points for ingredients.
- Numbered steps for instructions.
- Ask clarifying questions if anything is ambiguous.
Strictly avoid starting responses with: "Based on the knowledge base", or similar phrases.
Keep answers concise and helpful.
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