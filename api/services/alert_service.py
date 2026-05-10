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
        en utilisant le modèle ML AirSentinel (compute_interactive).
        Source identique à la carte — cohérence totale.
        """
        from api.routers.predictions import compute_interactive
        from api.schemas.prediction import ComputeInput

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
                row_raw = features_map.get(city_key, {})
                
                # Nettoyage des features pour le modèle (uniquement numériques)
                row_features = {}
                for k, v in row_raw.items():
                    if k in ["latitude", "longitude"]:
                        try: row_features[k] = float(v)
                        except: continue
                    if k in ["ville", "city", "date", "ville_key"]: continue
                    try:
                        val = float(v)
                        import math
                        row_features[k] = val if not math.isnan(val) else 0.0
                    except: continue

                # Prédiction ML
                prediction = compute_interactive(ComputeInput(
                    city=user.subscribed_city,
                    features=row_features
                ))

                pm25 = prediction.predicted_pm25
                logger.info(f"[AlertService] ML PM2.5={pm25:.2f} µg/m³ pour {user.email} @ {user.subscribed_city}")

                if pm25 > 15:
                    logger.info(f"[AlertService] SEUIL FRANCHI ({pm25:.2f}) → alerte {user.email}")
                    await EmailService.send_air_quality_alert(
                        email=user.email,
                        city=user.subscribed_city,
                        pm25=pm25,
                        level=prediction.level,
                        color=prediction.color,
                    )
                    if user.fcm_token:
                        try:
                            from api.services.notification_service import NotificationService
                            await NotificationService.send_air_quality_alert(
                                token=user.fcm_token,
                                city=user.subscribed_city,
                                pm25=pm25,
                                level=prediction.level,
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
        Utilise le modèle ML AirSentinel (identique à la carte).
        """
        from api.routers.predictions import compute_interactive
        from api.schemas.prediction import ComputeInput

        try:
            if not user.subscribed_city or not user.is_alerts_enabled:
                return

            features_map = _load_city_features_map()
            city_key = user.subscribed_city.lower().strip()
            row_raw = features_map.get(city_key, {})

            # Nettoyage
            row_features = {}
            for k, v in row_raw.items():
                if k in ["latitude", "longitude"]:
                    try: row_features[k] = float(v)
                    except: continue
                if k in ["ville", "city", "date", "ville_key"]: continue
                try:
                    val = float(v)
                    import math
                    row_features[k] = val if not math.isnan(val) else 0.0
                except: continue

            prediction = compute_interactive(ComputeInput(
                city=user.subscribed_city,
                features=row_features
            ))

            pm25 = prediction.predicted_pm25
            logger.info(f"[AlertService] IMMÉDIATE ML PM2.5={pm25:.2f} µg/m³ pour {user.email}")

            if pm25 > 15:
                await EmailService.send_air_quality_alert(
                    email=user.email,
                    city=user.subscribed_city,
                    pm25=pm25,
                    level=prediction.level,
                    color=prediction.color,
                )
                if user.fcm_token:
                    try:
                        from api.services.notification_service import NotificationService
                        await NotificationService.send_air_quality_alert(
                            token=user.fcm_token,
                            city=user.subscribed_city,
                            pm25=pm25,
                            level=prediction.level,
                        )
                    except Exception:
                        pass

                user.last_alert_sent = datetime.now(timezone.utc)
                await db.commit()

        except Exception as e:
            logger.error(f"[AlertService] Erreur alerte immédiate : {str(e)}")
