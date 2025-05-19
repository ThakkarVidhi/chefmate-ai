import re

def to_snake_case(s: str) -> str:
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

def parse_r_list_string(raw: str) -> list:
    # Remove c(...) wrapper and split on commas properly
    raw = raw.strip()
    if raw.startswith("c(") and raw.endswith(")"):
        raw = raw[2:-1]  # remove 'c(' and ')'
    
    # Split on comma, remove surrounding quotes and whitespace
    parts = [item.strip().strip('"').strip("'") for item in raw.split(",")]

    return parts

def clean_string_list(parts: str) -> list:
    # Remove empty strings
    parts = [p.lower() for p in parts if p]
    
    return parts

def parse_user_ingredients(input_str: str) -> list:
    return [re.sub(r'[^\w\s]', '', item.lower().strip()) for item in input_str.split(',') if item.strip()]

def combine_ingredients_with_quantities(quantities, ingredients):
    quantities = parse_r_list_string(quantities)
    
    if not isinstance(quantities, list) or not isinstance(ingredients, list):
        return []  # or return None if you prefer
    return [f"{q} {i}" for q, i in zip(quantities, ingredients)]