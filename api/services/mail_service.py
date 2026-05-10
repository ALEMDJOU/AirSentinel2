# api/services/mail_service.py

import httpx
import logging
from typing import Optional

from api.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def _send_email_brevo(to_email: str, subject: str, html_content: str):
        """Envoi d'email via l'API Brevo v3."""
        if not settings.BREVO_API_KEY:
            logger.warning("[Mail] BREVO_API_KEY non configuré. L'email est affiché dans les logs au lieu d'être envoyé.")
            logger.info(f"[SIMULATED BREVO MAIL] To: {to_email} | Subject: {subject}\nContent: {html_content[:200]}...")
            return

        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "accept": "application/json",
            "api-key": settings.BREVO_API_KEY,
            "content-type": "application/json"
        }
        
        payload = {
            "sender": {
                "name": settings.EMAILS_FROM_NAME,
                "email": settings.EMAILS_FROM_EMAIL
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code in [201, 200, 202]:
                    logger.info(f"[Mail] Email Brevo envoyé avec succès à {to_email}")
                else:
                    logger.error(f"[Mail] Erreur Brevo ({response.status_code}): {response.text}")
                    
        except Exception as e:
            logger.error(f"[Mail] Échec de l'envoi via Brevo : {str(e)}")

    @classmethod
    async def send_air_quality_alert(cls, email: str, city: str, pm25: float, level: str, color: str):
        """Envoie un mail d'alerte PM2.5 stylisé via Brevo."""
        subject = f"Alerte AirSentinel : Qualité de l'air {level} à {city}"
        
        html_template = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="text-align: center; margin-bottom: 25px;">
                <img src="https://raw.githubusercontent.com/ALEMDJOU/AirSentinel2/master/pwa/airsentinel/public/LogoAir.png" alt="AirSentinel Logo" style="height: 55px;">
            </div>
            <div style="max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 15px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
                <div style="background: {color}; padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">AirSentinel Alerts</h1>
                </div>
                <div style="padding: 40px; text-align: center;">
                    <p style="text-transform: uppercase; letter-spacing: 2px; font-weight: 800; color: #94a3b8; font-size: 12px; margin-bottom: 10px;">Alerte de Qualité de l'Air</p>
                    <h2 style="font-size: 40px; margin: 0; color: white;">{pm25} <span style="font-size: 16px; opacity: 0.5;">µg/m³</span></h2>
                    <p style="color: #64748b; font-size: 14px; margin-top: 5px;">Concentration de PM2.5 à <strong>{city}</strong></p>
                    
                    <div style="margin: 30px 0; padding: 15px; border-radius: 10px; background: {color}22; border: 1px solid {color}44; color: {color}; font-weight: bold; text-transform: uppercase;">
                        Status: {level}
                    </div>
                    
                    <p style="color: #94a3b8; line-height: 1.6; font-size: 15px;">
                        Nous avons détecté une dégradation de la qualité de l'air dans votre région. 
                        Veuillez limiter vos activités de plein air et fermer vos fenêtres si possible.
                    </p>
                    
                    <a href="{settings.FRONTEND_URL}/dashboard/predictions" 
                       style="display: inline-block; margin-top: 30px; padding: 15px 30px; background: #10b981; color: white; text-decoration: none; border-radius: 12px; font-weight: 900; text-transform: uppercase; font-size: 12px;">
                        Voir l'Analyse Complète
                    </a>
                </div>
                <div style="padding: 20px; background: #0f172a; text-align: center; font-size: 11px; color: #475569;">
                    &copy; 2026 AirSentinel Cameroon — Surveillance Intelligente. Tous droits réservés.
                </div>
            </div>
        </body>
        </html>
        """
        await cls._send_email_brevo(email, subject, html_template)

    @classmethod
    async def send_welcome_email(cls, email: str, name: str, city: str):
        """Envoie un mail de bienvenue stylisé lors de l'inscription."""
        subject = "Bienvenue sur AirSentinel : Surveillance de la qualité de l'air"
        
        html_template = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="text-align: center; margin-bottom: 25px;">
                <img src="https://raw.githubusercontent.com/ALEMDJOU/AirSentinel2/master/pwa/airsentinel/public/LogoAir.png" alt="AirSentinel Logo" style="height: 55px;">
            </div>
            <div style="max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 20px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 20px 50px rgba(0,0,0,0.5);">
                <div style="background: linear-gradient(135deg, #10b981, #0ea5e9); padding: 40px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 32px; font-weight: 900; letter-spacing: -1px;">Bienvenue, {name or 'Sentinel'} !</h1>
                </div>
                <div style="padding: 40px;">
                    <p style="color: #94a3b8; font-size: 16px; line-height: 1.6;">
                        Merci d'avoir rejoint <strong>AirSentinel</strong>, la première plateforme intelligente de surveillance de l'air au Cameroun.
                    </p>
                    
                    <div style="margin: 30px 0; padding: 20px; background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; border-radius: 8px;">
                        <h3 style="color: #10b981; margin-top: 0;">Votre abonnement local</h3>
                        <p style="color: #e2e8f0; margin-bottom: 0;">
                            Vous êtes actuellement abonné aux alertes pour la ville de <strong>{city}</strong>. 
                        </p>
                    </div>

                    <h3 style="color: white; margin-top: 30px;">Comment ça marche ?</h3>
                    <ul style="color: #94a3b8; padding-left: 20px; line-height: 1.8;">
                        <li><strong>Surveillance 24/7</strong> : Nos modèles d'IA analysent les données météo de votre ville en continu.</li>
                        <li><strong>Alertes Intelligentes</strong> : Si le taux de particules fines (PM2.5) dépasse le seuil de sécurité, vous recevrez un mail comme celui-ci.</li>
                        <li><strong>Conseils de santé</strong> : Chaque alerte est accompagnée de recommandations pour protéger vos proches.</li>
                    </ul>

                    <div style="text-align: center; margin-top: 40px;">
                        <a href="{settings.FRONTEND_URL}/dashboard" 
                           style="display: inline-block; padding: 18px 36px; background: #10b981; color: white; text-decoration: none; border-radius: 14px; font-weight: 900; text-transform: uppercase; font-size: 14px; box-shadow: 0 10px 20px rgba(16, 185, 129, 0.3);">
                            Accéder à mon tableau de bord
                        </a>
                    </div>
                </div>
                <div style="padding: 25px; background: #0f172a; text-align: center; font-size: 12px; color: #475569; border-top: 1px solid rgba(255,255,255,0.05);">
                    AirSentinel Cameroon — IndabaX 2026<br/>
                    Propulsé par l'IA au service de la santé publique.
                </div>
            </div>
        </body>
        </html>
        """
        await cls._send_email_brevo(email, subject, html_template)

    @classmethod
    async def send_broadcast_message(cls, email: str, name: str, subject: str, message: str):
        """Envoie un message de broadcast stylisé."""
        html_template = f"""
        <html>
        <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; padding: 20px;">
            <div style="text-align: center; margin-bottom: 25px;">
                <img src="https://raw.githubusercontent.com/ALEMDJOU/AirSentinel2/master/pwa/airsentinel/public/LogoAir.png" alt="AirSentinel Logo" style="height: 55px;">
            </div>
            <div style="max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 15px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1);">
                <div style="background: #10b981; padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0; font-size: 28px;">AirSentinel News</h1>
                </div>
                <div style="padding: 40px;">
                    <p style="color: #94a3b8; font-size: 14px; margin-bottom: 20px;">Bonjour {name or 'Sentinel'},</p>
                    
                    <p style="color: #f8fafc; line-height: 1.6; font-size: 16px;">
                        {message}
                    </p>
                    
                    <div style="text-align: center; margin-top: 40px;">
                        <a href="{settings.FRONTEND_URL}" 
                           style="display: inline-block; padding: 15px 30px; background: #3b82f6; color: white; text-decoration: none; border-radius: 12px; font-weight: 900; text-transform: uppercase; font-size: 12px;">
                            Accéder à AirSentinel
                        </a>
                    </div>
                </div>
                <div style="padding: 20px; background: #0f172a; text-align: center; font-size: 11px; color: #475569;">
                    &copy; 2026 AirSentinel Cameroon — Surveillance Intelligente. Tous droits réservés.
                </div>
            </div>
        </body>
        </html>
        """
        await cls._send_email_brevo(email, subject, html_template)
