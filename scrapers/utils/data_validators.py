
import pandas as pd
from typing import List, Dict, Any, Optional

def validate_dataframe(
    df: pd.DataFrame,
    required_columns: List[str],
    date_columns: Optional[List[str]] = None,
    numeric_columns: Optional[List[str]] = None
) -> bool:
    """Validate DataFrame structure and data types"""
    
    # Check required columns
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        print(f"Missing required columns: {missing_columns}")
        return False
    
    # Check for empty DataFrame
    if df.empty:
        print("DataFrame is empty")
        return False
    
    # Check date columns
    if date_columns:
        for col in date_columns:
            if col in df.columns:
                try:
                    pd.to_datetime(df[col])
                except:
                    print(f"Invalid date format in column: {col}")
                    return False
    
    # Check numeric columns
    if numeric_columns:
        for col in numeric_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except:
                    print(f"Invalid numeric format in column: {col}")
                    return False
    
    return True

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame by removing duplicates and nulls"""
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Remove rows where all values are null
    df = df.dropna(how='all')
    
    # Reset index
    df = df.reset_index(drop=True)
    
    return df
