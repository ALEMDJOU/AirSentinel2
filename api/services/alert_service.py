# api/services/alert_service.py
# Version finale : utilise le modele ML AirSentinel (compute_interactive) comme source unique de verite
# Cohérent avec la carte qui utilise également ce modèle.

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.models.user import User
from api.services.mail_service import EmailService

logger = logging.getLogger(__name__)


def _load_city_features_map() -> dict:
    """
    Charge le dataset et retourne un dict {ville_lower: features_dict}
    basé sur le dernier relevé réel par ville.
    Ces features alimentent le modèle ML, identique à la carte.
    """
    from api.services.data_service import get_dataframe
    try:
        df = get_dataframe()
        df_latest = df.sort_values("date").groupby("ville").last().reset_index()
        df_latest["ville_key"] = df_latest["ville"].str.lower().str.strip()
        result = {}
        for _, row in df_latest.iterrows():
            # On passe tout le dictionnaire de la ligne (lags, meteo, etc.)
            result[row["ville_key"]] = row.to_dict()
        return result
    except Exception as e:
        logger.error(f"[AlertService] Impossible de charger le dataset : {e}")
        return {}


class AlertService:

    @staticmethod
    async def process_alerts(db: AsyncSession):
        """
        Vérifie la qualité de l'air pour chaque utilisateur abonné
        en utilisant le modèle ML AirSentinel (meilleur_modele.pkl).
        """
        from api.services.prediction_service import predict_pm25
        from api.routers.carte import _pm25_level  # helper OMS 2021
        import math

        stmt = select(User).where(
            User.subscribed_city.isnot(None),
            User.subscribed_city != "",
            User.is_alerts_enabled == True
        )
        result = await db.execute(stmt)
        users = result.scalars().all()

        if not users:
            logger.info("[AlertService] Aucun utilisateur abonné.")
            return

        features_map = _load_city_features_map()

        for user in users:
            try:
                # Cool-down de 3 heures
                if user.last_alert_sent and (datetime.now(timezone.utc) - user.last_alert_sent) < timedelta(hours=3):
                    continue

                city_key = user.subscribed_city.lower().strip()
                latest_city_data = features_map.get(city_key, {})

                if not latest_city_data:
                    logger.warning(f"[AlertService] Aucune donnée pour {user.subscribed_city}")
                    continue

                # Nettoyage et prédiction hybride (RL + ARIMA)
                clean_features = {k: float(v) for k, v in latest_city_data.items() if isinstance(v, (int, float))}
                region = latest_city_data.get('region', 'Centre')
                pm25 = predict_pm25(clean_features, region=region)
                
                if pm25 <= 0 or math.isnan(pm25):
                    pm25 = float(latest_city_data.get("pm2_5_moyen", latest_city_data.get("pm25", 25.0)))

                level_key, color = _pm25_level(pm25)
                logger.info(f"[AlertService] ML Hybride PM2.5={pm25:.2f} µg/m³ pour {user.email} @ {user.subscribed_city} → {level_key}")

                if pm25 > 15:
                    logger.info(f"[AlertService] SEUIL FRANCHI ({pm25:.2f}) → alerte {user.email}")
                    await EmailService.send_air_quality_alert(
                        email=user.email,
                        city=user.subscribed_city,
                        pm25=pm25,
                        level=level_key,
                        color=color,
                    )
                    if user.fcm_token:
                        try:
                            from api.services.notification_service import NotificationService
                            await NotificationService.send_air_quality_alert(
                                token=user.fcm_token,
                                city=user.subscribed_city,
                                pm25=pm25,
                                level=level_key,
                            )
                        except Exception as push_err:
                            logger.error(f"[AlertService] Erreur push : {push_err}")

                    user.last_alert_sent = datetime.now(timezone.utc)
                    await db.commit()

            except Exception as e:
                logger.error(f"[AlertService] Erreur pour {user.email} : {str(e)}")

    @staticmethod
    async def trigger_immediate_alert(user: User, db: AsyncSession):
        """
        Alerte immédiate lors de l'inscription.
        Utilise le modèle ML Hybride (RL + ARIMA).
        """
        from api.services.prediction_service import predict_pm25
        from api.routers.carte import _pm25_level
        import math

        try:
            if not user.subscribed_city or not user.is_alerts_enabled:
                return

            features_map = _load_city_features_map()
            city_key = user.subscribed_city.lower().strip()
            latest_city_data = features_map.get(city_key, {})

            if not latest_city_data:
                return

            # Nettoyage
            clean_features = {k: float(v) for k, v in latest_city_data.items() if isinstance(v, (int, float))}
            region = latest_city_data.get('region', 'Centre')
            
            # Prédiction ML Hybride
            pm25 = predict_pm25(clean_features, region=region)
            if pm25 <= 0 or math.isnan(pm25):
                pm25 = float(latest_city_data.get("pm2_5_moyen", latest_city_data.get("pm25", 25.0)))

            level_key, color = _pm25_level(pm25)
            logger.info(f"[AlertService] IMMÉDIATE ML Hybride PM2.5={pm25:.2f} µg/m³ pour {user.email} → {level_key}")

            if pm25 > 15:
                await EmailService.send_air_quality_alert(
                    email=user.email,
                    city=user.subscribed_city,
                    pm25=pm25,
                    level=level_key,
                    color=color,
                )
                if user.fcm_token:
                    try:
                        from api.services.notification_service import NotificationService
                        await NotificationService.send_air_quality_alert(
                            token=user.fcm_token,
                            city=user.subscribed_city,
                            pm25=pm25,
                            level=level_key,
                        )
                    except Exception:
                        pass

                user.last_alert_sent = datetime.now(timezone.utc)
                await db.commit()

        except Exception as e:
            logger.error(f"[AlertService] Erreur alerte immédiate : {str(e)}")

