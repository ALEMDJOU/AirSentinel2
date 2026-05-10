import os
import pandas as pd
import numpy as np
import requests
import joblib
from datetime import datetime, timedelta
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Configuration Open-Meteo
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Liste des villes et coordonnées
CITIES = [
    {'ville': 'Abong-Mbang', 'region': 'Est', 'lat': 3.98, 'lon': 13.17},
    {'ville': 'Akonolinga', 'region': 'Centre', 'lat': 3.77, 'lon': 12.25},
    {'ville': 'Ambam', 'region': 'Sud', 'lat': 2.38, 'lon': 11.28},
    {'ville': 'Bafia', 'region': 'Centre', 'lat': 4.75, 'lon': 11.23},
    {'ville': 'Bafoussam', 'region': 'Ouest', 'lat': 5.48, 'lon': 10.42},
    {'ville': 'Bamenda', 'region': 'Nord-Ouest', 'lat': 5.96, 'lon': 10.16},
    {'ville': 'Batouri', 'region': 'Est', 'lat': 4.43, 'lon': 14.37},
    {'ville': 'Bertoua', 'region': 'Est', 'lat': 4.58, 'lon': 13.68},
    {'ville': 'Buea', 'region': 'Sud-Ouest', 'lat': 4.15, 'lon': 9.23},
    {'ville': 'Douala', 'region': 'Littoral', 'lat': 4.05, 'lon': 9.7},
    {'ville': 'Dschang', 'region': 'Ouest', 'lat': 5.45, 'lon': 10.07},
    {'ville': 'Ebolowa', 'region': 'Sud', 'lat': 2.92, 'lon': 11.15},
    {'ville': 'Edea', 'region': 'Littoral', 'lat': 3.8, 'lon': 10.13},
    {'ville': 'Foumban', 'region': 'Ouest', 'lat': 5.73, 'lon': 10.9},
    {'ville': 'Garoua', 'region': 'Nord', 'lat': 9.3, 'lon': 13.4},
    {'ville': 'Guider', 'region': 'Nord', 'lat': 9.93, 'lon': 13.95},
    {'ville': 'Kousseri', 'region': 'Extreme-Nord', 'lat': 12.08, 'lon': 15.03},
    {'ville': 'Kribi', 'region': 'Sud', 'lat': 2.95, 'lon': 9.92},
    {'ville': 'Kumba', 'region': 'Sud-Ouest', 'lat': 4.63, 'lon': 9.45},
    {'ville': 'Kumbo', 'region': 'Nord-Ouest', 'lat': 6.2, 'lon': 10.68},
    {'ville': 'Limbe', 'region': 'Sud-Ouest', 'lat': 4.02, 'lon': 9.22},
    {'ville': 'Loum', 'region': 'Littoral', 'lat': 4.72, 'lon': 9.73},
    {'ville': 'Mamfe', 'region': 'Sud-Ouest', 'lat': 5.75, 'lon': 9.32},
    {'ville': 'Maroua', 'region': 'Extreme-Nord', 'lat': 10.58, 'lon': 14.33},
    {'ville': 'Mbalmayo', 'region': 'Centre', 'lat': 3.52, 'lon': 11.5},
    {'ville': 'Mbengwi', 'region': 'Nord-Ouest', 'lat': 6.02, 'lon': 10.02},
    {'ville': 'Mbouda', 'region': 'Ouest', 'lat': 5.63, 'lon': 10.25},
    {'ville': 'Meiganga', 'region': 'Adamaoua', 'lat': 6.52, 'lon': 14.3},
    {'ville': 'Mokolo', 'region': 'Extreme-Nord', 'lat': 10.74, 'lon': 13.8},
    {'ville': 'Ngaoundere', 'region': 'Adamaoua', 'lat': 7.32, 'lon': 13.58},
    {'ville': 'Nkongsamba', 'region': 'Littoral', 'lat': 4.95, 'lon': 9.93},
    {'ville': 'Poli', 'region': 'Nord', 'lat': 8.48, 'lon': 13.25},
    {'ville': 'Sangmelima', 'region': 'Sud', 'lat': 2.93, 'lon': 11.98},
    {'ville': 'Tibati', 'region': 'Adamaoua', 'lat': 6.47, 'lon': 12.63},
    {'ville': 'Tignere', 'region': 'Adamaoua', 'lat': 7.37, 'lon': 12.65},
    {'ville': 'Touboro', 'region': 'Nord', 'lat': 7.77, 'lon': 15.37},
    {'ville': 'Wum', 'region': 'Nord-Ouest', 'lat': 6.38, 'lon': 10.07},
    {'ville': 'Yagoua', 'region': 'Extreme-Nord', 'lat': 10.33, 'lon': 15.23},
    {'ville': 'Yaounde', 'region': 'Centre', 'lat': 3.87, 'lon': 11.52},
    {'ville': 'Yokadouma', 'region': 'Est', 'lat': 3.52, 'lon': 15.05}
]

DATASET_PATH = "data/processed/dataset_final.parquet"

def get_air_quality_level(pm25):
    if pm25 <= 12: return "BON", "#4CAF50"
    if pm25 <= 35.4: return "MODERE", "#FFC107"
    if pm25 <= 55.4: return "SEVERE", "#FF9800"
    if pm25 <= 150.4: return "DANGEREUX", "#FF5722"
    return "CRITIQUE", "#B71C1C"

def fetch_data(villes_info, start_date, end_date):
    all_data = []
    for city in villes_info:
        try:
            # Weather
            w_res = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params={
                "latitude": city['lat'], "longitude": city['lon'], "start_date": start_date, "end_date": end_date,
                "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", 
                          "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean",
                          "sunrise", "sunset", "daylight_duration", "sunshine_duration", "precipitation_sum", 
                          "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", 
                          "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", 
                          "et0_fao_evapotranspiration"], "timezone": "auto"
            })[0].Daily()
            
            # AQ
            aq_res = openmeteo.weather_api("https://air-quality-api.open-meteo.com/v1/air-quality", params={
                "latitude": city['lat'], "longitude": city['lon'], "start_date": start_date, "end_date": end_date,
                "hourly": ["pm2_5", "pm10", "dust", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone", "uv_index", "us_aqi"],
                "timezone": "auto"
            })[0].Hourly()

            # Weather DF
            d_w = pd.date_range(start=pd.to_datetime(w_res.Time(), unit="s"), end=pd.to_datetime(w_res.TimeEnd(), unit="s"), freq=pd.Timedelta(seconds=w_res.Interval()), inclusive="left")
            df_w = pd.DataFrame({"date": d_w})
            for i, col in enumerate(["weather_code", "temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "apparent_temperature_max", "apparent_temperature_min", "apparent_temperature_mean"]):
                df_w[col] = w_res.Variables(i).ValuesAsNumpy()
            df_w["sunrise"] = pd.to_datetime(w_res.Variables(7).ValuesAsNumpy(), unit='s').strftime('%Y-%m-%d %H:%M')
            df_w["sunset"] = pd.to_datetime(w_res.Variables(8).ValuesAsNumpy(), unit='s').strftime('%Y-%m-%d %H:%M')
            for i, col in enumerate(["daylight_duration", "sunshine_duration", "precipitation_sum", "rain_sum", "snowfall_sum", "precipitation_hours", "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum", "et0_fao_evapotranspiration"], 9):
                df_w[col] = w_res.Variables(i).ValuesAsNumpy()

            # AQ DF
            d_aq = pd.date_range(start=pd.to_datetime(aq_res.Time(), unit="s"), end=pd.to_datetime(aq_res.TimeEnd(), unit="s"), freq=pd.Timedelta(seconds=aq_res.Interval()), inclusive="left")
            df_aq_h = pd.DataFrame({"date": d_aq})
            for i, col in enumerate(["pm2_5", "pm10", "dust", "co", "no2", "so2", "ozone", "uv", "aqi"]):
                df_aq_h[col] = aq_res.Variables(i).ValuesAsNumpy()
            
            df_aq_d = df_aq_h.groupby(df_aq_h['date'].dt.date).agg({'pm2_5':['mean','max'],'pm10':'mean','dust':'mean','co':'mean','no2':'mean','so2':'mean','ozone':'mean','uv':'mean','aqi':'mean'})
            df_aq_d.columns = ['pm2_5_moyen','pm2_5_max','pm10_moyen','dust_moyen','co_moyen','no2_moyen','so2_moyen','ozone_moyen','uv_moyen','us_aqi_moyen']
            df_aq_d = df_aq_d.reset_index().rename(columns={'index':'date'})
            df_aq_d['date'] = pd.to_datetime(df_aq_d['date']).dt.normalize()
            df_w['date'] = df_w['date'].dt.normalize()

            df_city = pd.merge(df_w, df_aq_d, on="date", how="inner")
            df_city["ville"], df_city["region"], df_city["latitude"], df_city["longitude"] = city['ville'], city['region'], city['lat'], city['lon']
            df_city["polluant_dominant"] = "pm2_5"
            df_city["niveau_alerte"] = df_city["pm2_5_moyen"].apply(lambda x: get_air_quality_level(x)[0])
            all_data.append(df_city)
            print(f"Fetch OK: {city['ville']}")
        except Exception as e:
            print(f"Error {city['ville']}: {str(e)}")
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def process_features(df, df_old):
    df_c = pd.concat([df_old, df], ignore_index=True).drop_duplicates(['date', 'ville'], keep='last').sort_values(['ville', 'date'])
    for l in [1, 3, 7]: df_c[f'pm2_5_lag_{l}j'] = df_c.groupby('ville')['pm2_5_moyen'].shift(l)
    for f in [7, 30]: df_c[f'pm2_5_moy_{f}j'] = df_c.groupby('ville')['pm2_5_moyen'].transform(lambda x: x.rolling(window=f, min_periods=1).mean())
    df_c['pm2_5_log'], df_c['annee'], df_c['mois'], df_c['jour_annee'] = np.log1p(df_c['pm2_5_moyen']), df_c['date'].dt.year, df_c['date'].dt.month, df_c['date'].dt.dayofyear
    df_c['saison_code'] = df_c['date'].dt.month.map({12:0,1:0,2:0,3:1,4:1,5:2,6:2,7:2,8:2,9:2,10:2,11:1})
    def n(s): return (s-s.min())/(s.max()-s.min()) if s.max()!=s.min() else 0
    df_c['indice_stagnation'] = 0.4*n(df_c['temperature_2m_max']) + 0.4*(1-n(df_c['wind_speed_10m_max']))
    df_c['harmattan_intense'] = ((df_c['dust_moyen']>50)&(df_c['saison_code']==0)).astype(int)
    df_c['episode_feux'] = ((df_c['co_moyen']>500)&(df_c['saison_code']==0)).astype(int)
    for r in ['Adamaoua','Centre','Est','Extreme-Nord','Littoral','Nord','Nord-Ouest','Ouest','Sud','Sud-Ouest']: df_c[f'region_{r}'] = (df_c['region']==r).astype(int)
    return df_c

def compute_irs(df):
    try:
        sc, pca, cols = joblib.load('models/scaler.pkl'), joblib.load('models/pca_irs.pkl'), joblib.load('models/cols_irs.pkl')
        X = df[cols].fillna(0)
        df['IRS'] = (pca.transform(sc.transform(X))[:, 0] + 5) * 10 # Normalisation approx
        df['niveau_sanitaire'] = df['IRS'].apply(lambda x: "BON" if x<25 else "MODERE" if x<50 else "ELEVE" if x<75 else "CRITIQUE")
    except:
        df['IRS'], df['niveau_sanitaire'] = df['pm2_5_moyen']*1.5, df['niveau_alerte']
    return df

def main():
    if not os.path.exists(DATASET_PATH): return
    df_old = pd.read_parquet(DATASET_PATH)
    start = (df_old['date'].max() + timedelta(days=1)).strftime('%Y-%m-%d')
    end = datetime.now().strftime('%Y-%m-%d')
    if start > end: return
    df_new = fetch_data(CITIES, start, end)
    if not df_new.empty:
        df_f = compute_irs(process_features(df_new, df_old))
        df_f.to_parquet(DATASET_PATH, index=False)
        print("Update Success")

if __name__ == "__main__": main()
