import pandas as pd
import re
from app.utils.helper import to_snake_case, parse_r_list_string, clean_string_list, parse_user_ingredients, combine_ingredients_with_quantities


def load_recipe_data(file_path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading recipe data: {e}")
        return pd.DataFrame()
    
def clean_recipe_data(df: pd.DataFrame) -> pd.DataFrame:

    # Rename columns to snake_case
    df.columns = [to_snake_case(col) for col in df.columns]
    print(f"Renamed columns: {df.columns.tolist()}")

    # Drop duplicates
    df = df.drop_duplicates()
    print(f"DataFrame shape after dropping duplicates: {df.shape}")

    # Drop rows with missing values in 'recipe_ingredient_parts' or 'recipe_instructions'
    df = df.dropna(subset=['recipe_ingredient_parts', 'recipe_instructions'])
    print(f"DataFrame shape after dropping missing values: {df.shape}")
    
    df['recipe_ingredient_quantities'] = df['recipe_ingredient_quantities'].fillna('[]')

    # Store raw ingredients separately
    df['ingredients_raw'] = df['recipe_ingredient_parts'].apply(parse_r_list_string)
    df['ingredients_cleaned'] = df['ingredients_raw'].apply(clean_string_list)
    
    print(df.loc[1].ingredients_raw)
    print(type(df.loc[1].ingredients_raw))
    
    df['ingredients_with_quantities'] = df.apply(
        lambda row: combine_ingredients_with_quantities(row['recipe_ingredient_quantities'], row['ingredients_raw']),
        axis=1
    )

    print("Sample cleaned ingredients:")
    print(df[['ingredients_raw', 'ingredients_cleaned', 'ingredients_with_quantities']].head())

    # Convert date
    if 'date_published' in df.columns:
        df['date_published'] = pd.to_datetime(df['date_published'], errors='coerce')

    # Fill missing review/rating
    df['review_count'] = df['review_count'].fillna(0).astype(int)
    df['aggregated_rating'] = df['aggregated_rating'].fillna(0).astype(float)

    print(df.head())
    return df
