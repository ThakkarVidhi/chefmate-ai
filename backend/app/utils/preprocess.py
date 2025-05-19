import pandas as pd
from typing import Optional
from app.utils.helper import (
    to_snake_case,
    parse_r_list_string,
    clean_string_list,
    combine_ingredients_with_quantities
)


def load_recipe_data(file_path: str) -> pd.DataFrame:
    """Load recipe data from a CSV file into a DataFrame."""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading recipe data: {e}")
        return pd.DataFrame()


def clean_recipe_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and transform the raw recipe DataFrame for analysis."""

    # Rename columns to snake_case
    df.columns = [to_snake_case(col) for col in df.columns]
    print(f"Renamed columns: {df.columns.tolist()}")

    # Drop duplicates and rows with missing critical fields
    df.drop_duplicates(inplace=True)
    print(f"Shape after dropping duplicates: {df.shape}")

    df.dropna(subset=['recipe_ingredient_parts', 'recipe_instructions'], inplace=True)
    print(f"Shape after dropping missing recipe parts/instructions: {df.shape}")

    # Fill missing quantities with empty list strings
    df['recipe_ingredient_quantities'] = df['recipe_ingredient_quantities'].fillna('[]')

    # Parse ingredients
    df['ingredients_raw'] = df['recipe_ingredient_parts'].apply(parse_r_list_string)
    df['ingredients_cleaned'] = df['ingredients_raw'].apply(clean_string_list)

    # Combine ingredients with their quantities
    df['ingredients_with_quantities'] = df.apply(
        lambda row: combine_ingredients_with_quantities(
            row['recipe_ingredient_quantities'], row['ingredients_raw']
        ),
        axis=1
    )

    # Debugging outputs (can be removed in production)
    print("Sample cleaned ingredients:")
    print(df[['ingredients_raw', 'ingredients_cleaned', 'ingredients_with_quantities']].head())

    # Convert date columns safely
    if 'date_published' in df.columns:
        df['date_published'] = pd.to_datetime(df['date_published'], errors='coerce')

    # Fill in ratings and review count with sensible defaults
    df['review_count'] = df['review_count'].fillna(0).astype(int)
    df['aggregated_rating'] = df['aggregated_rating'].fillna(0.0).astype(float)

    print("Final cleaned DataFrame:")
    print(df.head())

    return df