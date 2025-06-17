from difflib import SequenceMatcher
from typing import List, Union, Dict
import pandas as pd
import numpy as np
import os
import re

def to_snake_case(s: str) -> str:
    """Convert CamelCase or PascalCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', s).lower()

def parse_r_list_string(raw: Union[str, float]) -> List[str]:
    """
    Parse an R-style list string (e.g., 'c("a", "b", "c")') into a Python list.
    Returns an empty list if input is not a valid string.
    """
    if not isinstance(raw, str):
        return []

    raw = raw.strip()
    if raw.startswith("c(") and raw.endswith(")"):
        raw = raw[2:-1]

    return re.findall(r'"(.*?)"', raw)


def clean_string_list(items: List[str]) -> List[str]:
    """Clean a list of strings: remove empty entries and lowercase everything."""
    return [item.lower() for item in items if item]


def parse_user_ingredients(input_str: str) -> List[str]:
    """Convert user input string of ingredients into a cleaned list."""
    return [
        re.sub(r'[^\w\s]', '', item.lower().strip())
        for item in input_str.split(',') if item.strip()
    ]


def combine_ingredients_with_quantities(quantities_raw: Union[str, float], ingredients: Union[List[str], float]) -> List[str]:
    """
    Combine quantities and ingredients into a list of formatted strings.
    If lengths mismatch or input is invalid, returns an empty list.
    """
    quantities = parse_r_list_string(quantities_raw)

    if not isinstance(quantities, list) or not isinstance(ingredients, list):
        return []

    return [f"{q} {i}".strip() for q, i in zip(quantities, ingredients)]

# Function to convert ISO 8601 duration to "HH:MM"
def parse_iso_duration(duration):
    if not isinstance(duration, str) or not duration.strip():
        return None

    # Try to parse ISO 8601 format like PT2H15M
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration.strip())
    if not match:
        return None

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0

    return f"{hours:02d}:{minutes:02d}"

def load_dataframe(pickle_path: str) -> pd.DataFrame:
    """
    Load DataFrame from a pickle file.
    """
    if not os.path.exists(pickle_path):
        raise FileNotFoundError(f"Pickle file not found at: {pickle_path}")

    df = pd.read_pickle(pickle_path)
    if df.empty:
        raise ValueError("Loaded DataFrame is empty.")
    
    return df

def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj

def clean_streamed_text(text: str) -> str:
    text = re.sub(r'[ ]{2,}', ' ', text)  
    text = re.sub(r'\s+\n', '\n', text)   
    text = re.sub(r'\n\s+', '\n', text)   
    return text

def fuzzy_match(a, b):
    return SequenceMatcher(None, a, b).ratio()

def interpret_user_selection(user_input: str, suggested_recipes: List[Dict]) -> int:
    user_input = user_input.lower().strip()
    print(f"[DEBUG] Interpreting user input for selection: '{user_input}'")

    # Check if it's about a cooking step instead of recipe selection
    if re.search(r"(step|instruction)\s*(\d+|first|second|third|one|two|three)", user_input):
        print("[DEBUG] Detected instruction-related phrase. Skipping recipe selection.")
        return None

    # Define numeric/ordinal mapping
    position_aliases = {
        "first": 0, "1st": 0, "one": 0, "1": 0,
        "second": 1, "2nd": 1, "two": 1, "2": 1,
        "third": 2, "3rd": 2, "three": 2, "3": 2
    }

    # Try to match numeric position regardless of keyword
    for word, idx in position_aliases.items():
        if re.search(rf"\b{word}\b", user_input):
            if idx < len(suggested_recipes):
                print(f"[DEBUG] Matched positional keyword '{word}' to index {idx}")
                return idx
            else:
                print(f"[DEBUG] Matched positional keyword '{word}', but index {idx} is out of range.")
                return None

    # Try fuzzy matching with recipe titles
    best_match = None
    best_score = 0.0
    for i, recipe in enumerate(suggested_recipes):
        score = fuzzy_match(recipe["name"].lower(), user_input)
        print(f"[DEBUG] Fuzzy match score for '{recipe['name']}' is {score:.2f}")
        if score > best_score and score > 0.6:
            best_match = i
            best_score = score

    if best_match is not None:
        print(f"[DEBUG] Selected recipe index {best_match} via fuzzy title match")
    else:
        print("[DEBUG] No recipe matched via position or fuzzy title match")

    return best_match

def is_requesting_new_suggestions(user_input: str) -> bool:
    patterns = [
        r"more (suggestions|recipes|options|choices)",
        r"another (suggestion|option|recipe)",
        r"show (me )?(something )?else",
        r"different (recipe|option|suggestion)",
        r"can i get.*(different|more|new)",
        r"new (recipes|suggestions)",
    ]
    user_input = user_input.lower()
    return any(re.search(pat, user_input) for pat in patterns)