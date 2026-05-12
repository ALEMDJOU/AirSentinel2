import pandas as pd
from datetime import datetime

dataset_path = "data/processed/dataset_final.parquet"

try:
    df = pd.read_parquet(dataset_path)
    print(f"Dataset columns: {df.columns.tolist()}")
    if 'date' in df.columns:
        print(f"Min date: {df['date'].min()}")
        print(f"Max date: {df['date'].max()}")
        print(f"Last 5 rows for Yaounde:")
        print(df[df['ville'] == 'Yaounde'].sort_values('date').tail(5)[['date', 'ville', 'pm2_5_moyen']])
    else:
        print("Date column not found")
except Exception as e:
    print(f"Error: {e}")
