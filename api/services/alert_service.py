# api/services/alert_service.py

from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from api.models.user import User
from api.services.mail_service import EmailService

logger = logging.getLogger(__name__)


def _get_pm25_level_from_raw(pm25: float):
    """
    Retourne (label, couleur) à partir du PM2.5 brut.
    Seuils alignés sur get_air_quality_level() dans update_daily.py et la carte.
    """
    if pm25 <= 12:
        return "BON", "#4CAF50"
    elif pm25 <= 35.4:
        return "MODÉRÉ", "#FFC107"
    elif pm25 <= 55.4:
        return "SÉVÈRE", "#FF9800"
    elif pm25 <= 150.4:
        return "DANGEREUX", "#FF5722"
    else:
        return "CRITIQUE", "#B71C1C"


def _load_city_pm25_map() -> dict:
    """
    Source de vérité unique : le dernier relevé par ville depuis le parquet,
    identique à ce qu'affiche la carte.
    """
    from api.services.data_service import get_dataframe
    try:
        df = get_dataframe()
        df_latest = df.sort_values("date").groupby("ville").last().reset_index()
        df_latest["ville_key"] = df_latest["ville"].str.lower().str.strip()
        return df_latest.set_index("ville_key").to_dict(orient="index")
    except Exception as e:
        logger.error(f"[AlertService] Impossible de charger le dataset : {e}")
        return {}


class AlertService:

    @staticmethod
    async def process_alerts(db: AsyncSession):
        """
        Vérifie les PM2.5 RÉELS (parquet) pour chaque utilisateur abonné.
        Source identique à la carte — garantit la cohérence carte ↔ emails.
        """
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

        data_map = _load_city_pm25_map()

        for user in users:
            try:
                # Cool-down de 3 heures
                if user.last_alert_sent and (datetime.now(timezone.utc) - user.last_alert_sent) < timedelta(hours=3):
                    continue

                city_key = user.subscribed_city.lower().strip()

                if city_key not in data_map:
                    logger.warning(f"[AlertService] Ville inconnue dans le dataset : {user.subscribed_city}")
                    continue

                # PM2.5 RÉEL — même source que la carte
                pm25 = float(data_map[city_key].get("pm2_5_moyen", 0.0))
                level, color = _get_pm25_level_from_raw(pm25)

                logger.info(f"[AlertService] PM2.5 réel={pm25:.2f} µg/m³ pour {user.email} @ {user.subscribed_city}")

                if pm25 > 15:
                    logger.info(f"[AlertService] SEUIL FRANCHI ({pm25:.2f} µg/m³) → envoi alerte {user.email}")

                    await EmailService.send_air_quality_alert(
                        email=user.email,
                        city=user.subscribed_city,
                        pm25=pm25,
                        level=level,
                        color=color,
                    )

                    if user.fcm_token:
                        try:
                            from api.services.notification_service import NotificationService
                            await NotificationService.send_air_quality_alert(
                                token=user.fcm_token,
                                city=user.subscribed_city,
                                pm25=pm25,
                                level=level,
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
        Déclenche une vérification immédiate pour un utilisateur lors de son inscription.
        Utilise le PM2.5 RÉEL du parquet (même source que la carte).
        """
        try:
            if not user.subscribed_city or not user.is_alerts_enabled:
                return

            data_map = _load_city_pm25_map()
            city_key = user.subscribed_city.lower().strip()

            if city_key not in data_map:
                logger.warning(f"[AlertService] Ville inconnue pour alerte immédiate : {user.subscribed_city}")
                return

            pm25 = float(data_map[city_key].get("pm2_5_moyen", 0.0))
            level, color = _get_pm25_level_from_raw(pm25)

            logger.info(f"[AlertService] ALERTE IMMÉDIATE PM2.5={pm25:.2f} µg/m³ pour {user.email}")

            if pm25 > 15:
                await EmailService.send_air_quality_alert(
                    email=user.email,
                    city=user.subscribed_city,
                    pm25=pm25,
                    level=level,
                    color=color,
                )

                if user.fcm_token:
                    try:
                        from api.services.notification_service import NotificationService
                        await NotificationService.send_air_quality_alert(
                            token=user.fcm_token,
                            city=user.subscribed_city,
                            pm25=pm25,
                            level=level,
                        )
                    except Exception:
                        pass

                user.last_alert_sent = datetime.now(timezone.utc)
                await db.commit()

        except Exception as e:
            logger.error(f"[AlertService] Erreur alerte immédiate : {str(e)}")
