# api/services/alert_service.py

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.models.user import User
from api.services.mail_service import EmailService

logger = logging.getLogger(__name__)

# Features moyennes réalistes par ville (basées sur les données IndabaX Cameroun)
# Reflètent les conditions typiques qui produisent des alertes pour les villes polluées
CITY_FEATURES = {
    "douala":       {"dust": 55.0, "co": 25.0, "uv": 6.0, "temp": 29.0, "humidity": 80.0, "ozone": 45.0},
    "yaoundé":      {"dust": 40.0, "co": 18.0, "uv": 5.5, "temp": 24.0, "humidity": 75.0, "ozone": 40.0},
    "yaounde":      {"dust": 40.0, "co": 18.0, "uv": 5.5, "temp": 24.0, "humidity": 75.0, "ozone": 40.0},
    "garoua":       {"dust": 90.0, "co": 20.0, "uv": 8.0, "temp": 38.0, "humidity": 30.0, "ozone": 55.0},
    "maroua":       {"dust": 110.0, "co": 22.0, "uv": 9.0, "temp": 40.0, "humidity": 20.0, "ozone": 60.0},
    "ngaoundéré":   {"dust": 60.0, "co": 15.0, "uv": 7.0, "temp": 22.0, "humidity": 65.0, "ozone": 50.0},
    "ngaoundere":   {"dust": 60.0, "co": 15.0, "uv": 7.0, "temp": 22.0, "humidity": 65.0, "ozone": 50.0},
    "bafoussam":    {"dust": 35.0, "co": 12.0, "uv": 5.0, "temp": 20.0, "humidity": 70.0, "ozone": 38.0},
    "bamenda":      {"dust": 38.0, "co": 13.0, "uv": 5.0, "temp": 22.0, "humidity": 72.0, "ozone": 38.0},
    "bertoua":      {"dust": 50.0, "co": 14.0, "uv": 6.0, "temp": 26.0, "humidity": 78.0, "ozone": 42.0},
    "kribi":        {"dust": 20.0, "co": 8.0,  "uv": 7.0, "temp": 27.0, "humidity": 85.0, "ozone": 30.0},
    "ebolowa":      {"dust": 25.0, "co": 9.0,  "uv": 5.5, "temp": 25.0, "humidity": 80.0, "ozone": 32.0},
    "touboro":      {"dust": 75.0, "co": 18.0, "uv": 8.5, "temp": 36.0, "humidity": 35.0, "ozone": 52.0},
    "buéa":         {"dust": 18.0, "co": 7.0,  "uv": 5.0, "temp": 22.0, "humidity": 88.0, "ozone": 28.0},
    "buea":         {"dust": 18.0, "co": 7.0,  "uv": 5.0, "temp": 22.0, "humidity": 88.0, "ozone": 28.0},
}
# Features par défaut pour les villes non listées
DEFAULT_FEATURES = {"dust": 50.0, "co": 15.0, "uv": 6.0, "temp": 30.0, "humidity": 60.0, "ozone": 42.0}


class AlertService:
    @staticmethod
    async def process_alerts(db: AsyncSession):
        """
        Vérifie les PM2.5 pour chaque utilisateur abonné en utilisant les données RÉELLES du dataset.
        """
        # 1. Récupérer les utilisateurs abonnés avec alertes actives
        stmt = select(User).where(
            User.subscribed_city.isnot(None),
            User.subscribed_city != "",
            User.is_alerts_enabled == True
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            logger.info("[AlertService] Aucun utilisateur abonné pour le moment.")
            return

        # 2. Charger les dernières données réelles du dataset
        from api.services.data_service import get_dataframe
        try:
            df = get_dataframe()
            # On s'assure d'avoir les données les plus récentes par ville
            df_latest = df.sort_values("date").groupby("ville").last().reset_index()
            # On met les noms de villes en minuscules pour faciliter la recherche
            df_latest["ville_key"] = df_latest["ville"].str.lower().str.strip()
            data_map = df_latest.set_index("ville_key").to_dict(orient="index")
        except Exception as e:
            logger.error(f"[AlertService] Impossible de charger le dataset réel : {e}. Fallback sur les moyennes.")
            data_map = {}

        # Import ici pour éviter un import circulaire
        from api.routers.predictions import compute_interactive
        from api.schemas.prediction import ComputeInput

        for user in users:
            try:
                # 3. Cool-down de 3 heures
                if user.last_alert_sent and (datetime.now(timezone.utc) - user.last_alert_sent) < timedelta(hours=3):
                    continue

                city_key = user.subscribed_city.lower().strip()
                
                # 4. Priorité aux données réelles du jour, sinon fallback sur les CITY_FEATURES
                if city_key in data_map:
                    real_data = data_map[city_key]
                    features = {
                        "dust": float(real_data.get("dust_moyen", 50.0)),
                        "co": float(real_data.get("co_moyen", 15.0)),
                        "uv": float(real_data.get("uv_moyen", 6.0)),
                        "temp": float(real_data.get("temperature_2m_mean", 25.0)),
                        "humidity": float(real_data.get("humidity_moyen", 60.0)), # Note: check column name in update_daily
                        "ozone": float(real_data.get("ozone_moyen", 40.0))
                    }
                    logger.info(f"[AlertService] Utilisation des données RÉELLES pour {user.email} @ {user.subscribed_city}")
                else:
                    features = CITY_FEATURES.get(city_key, DEFAULT_FEATURES)
                    logger.info(f"[AlertService] Fallback sur moyennes pour {user.email} @ {user.subscribed_city}")

                prediction = compute_interactive(ComputeInput(city=user.subscribed_city, features=features))
                
                # 5. Alerte si PM2.5 > 15 µg/m³
                if prediction.predicted_pm25 > 15:
                    logger.info(f"[AlertService] SEUIL FRANCHI ({prediction.predicted_pm25} µg/m³) pour {user.email}")

                    # Envoi Email
                    await EmailService.send_air_quality_alert(
                        email=user.email,
                        city=user.subscribed_city,
                        pm25=prediction.predicted_pm25,
                        level=prediction.level,
                        color=prediction.color,
                    )

                    # Envoi Push
                    if user.fcm_token:
                        try:
                            from api.services.notification_service import NotificationService
                            await NotificationService.send_air_quality_alert(
                                token=user.fcm_token,
                                city=user.subscribed_city,
                                pm25=prediction.predicted_pm25,
                                level=prediction.level,
                            )
                        except Exception as push_err:
                            logger.error(f"[AlertService] Erreur push : {push_err}")

                    user.last_alert_sent = datetime.now(timezone.utc)
                    await db.commit()

            except Exception as e:
                logger.error(f"[AlertService] Erreur pour {user.email} : {str(e)}")
