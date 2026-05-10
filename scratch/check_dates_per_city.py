import pandas as pd
df = pd.read_parquet("data/processed/dataset_final.parquet")
# Shift dates as in data_service
max_date = df['date'].max()
today = pd.Timestamp.now().normalize()
delta = today - max_date
df['date'] = df['date'] + delta

villes = ["Bafoussam", "Douala", "Yaounde"]
for v in villes:
    city_df = df[df['ville'].str.lower() == v.lower()]
    print(f"\n=== {v} ===")
    print(city_df[['date', 'pm2_5_moyen']].sort_values('date').tail(5))
