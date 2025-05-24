import re
from typing import Literal, Dict

IntentType = Literal[
    "specific_recipe",
    "recipe_generation",
    "ingredient_search",
    "step_navigation",
    "diet_filter",
    "nutrition_info",
    "time_filter",
    "rating_filter",
    "unclear"
]

class IntentDetector:
    def __init__(self):
        self.recipe_keywords = ["recipe", "make", "cook", "prepare", "how to"]
        self.ingredient_keywords = ["have", "with", "using", "ingredients"]
        self.step_keywords = ["next step", "what's next", "then", "after that"]
        self.diet_keywords = ["vegan", "vegetarian", "gluten", "keto", "halal", "diet"]
        self.nutrition_keywords = ["calories", "nutrition", "protein", "carbs"]
        self.time_keywords = ["quick", "under", "minutes", "fast", "less than"]
        self.rating_keywords = ["top", "best", "highest rated", "popular"]

    def detect_intent(self, user_input: str) -> Dict[str, str]:
        print(user_input)
        user_input = user_input.lower()

        # --- Specific Recipe ---
        if re.search(r"(recipe for|how to make|tell me about)\s+[a-z ]+", user_input):
            return {"intent": "specific_recipe"}

        # --- Ingredient-Based Search ---
        if any(keyword in user_input for keyword in self.ingredient_keywords) and ',' in user_input:
            return {"intent": "ingredient_search"}

        # --- Recipe Generation ---
        if any(kw in user_input for kw in self.recipe_keywords) and "recipe" in user_input:
            return {"intent": "recipe_generation"}

        # --- Step Navigation ---
        if any(kw in user_input for kw in self.step_keywords):
            return {"intent": "step_navigation"}

        # --- Dietary Filter ---
        if any(kw in user_input for kw in self.diet_keywords):
            return {"intent": "diet_filter"}

        # --- Nutrition Info ---
        if any(kw in user_input for kw in self.nutrition_keywords):
            return {"intent": "nutrition_info"}

        # --- Time Filter ---
        if any(kw in user_input for kw in self.time_keywords):
            return {"intent": "time_filter"}

        # --- Rating Filter ---
        if any(kw in user_input for kw in self.rating_keywords):
            return {"intent": "rating_filter"}

        # --- Default Case ---
        return {"intent": "unclear"}