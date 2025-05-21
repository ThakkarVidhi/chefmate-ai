import re
from typing import List, Union

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

    # Extract values between quotes using regex to preserve commas inside quotes
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
    # Check that duration is a valid string
    if not isinstance(duration, str) or not duration.strip():
        return None

    # Try to parse ISO 8601 format like PT2H15M
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", duration.strip())
    if not match:
        return None

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0

    return f"{hours:02d}:{minutes:02d}"