import os
import time
import pandas as pd
from pathlib import Path
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Mock settings before any imports that trigger get_settings()
os.environ["DATABASE_URL"] = "postgresql://mock"
os.environ["DATABASE_URL_SYNC"] = "postgresql://mock"
os.environ["SUPABASE_URL"] = "https://mock"
os.environ["SUPABASE_KEY"] = "mock"
os.environ["SECRET_KEY"] = "mock"

from api.services.data_service import get_dataframe

dataset_path = "data/processed/dataset_final.parquet"

def test_reload():
    print("--- Initial load ---")
    df1 = get_dataframe()
    print(f"Loaded {len(df1)} rows")
    
    print("\n--- Second load (should be from cache) ---")
    df2 = get_dataframe()
    print(f"Loaded {len(df2)} rows")
    
    # Touch the file to update mtime
    print("\n--- Touching the file ---")
    os.utime(dataset_path, None)
    
    print("\n--- Third load (should RELOAD) ---")
    df3 = get_dataframe()
    print(f"Loaded {len(df3)} rows")

if __name__ == "__main__":
    # Mock settings if needed, but data_service already imports them
    # Ensure env vars are set if .env is missing or incomplete
    os.environ["DATABASE_URL"] = "postgresql://mock"
    os.environ["DATABASE_URL_SYNC"] = "postgresql://mock"
    os.environ["SUPABASE_URL"] = "https://mock"
    os.environ["SUPABASE_KEY"] = "mock"
    os.environ["SECRET_KEY"] = "mock"
    
    test_reload()
