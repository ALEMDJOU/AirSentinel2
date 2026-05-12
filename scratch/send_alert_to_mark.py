import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

# Configuration des variables d'environnement (Indispensable avant imports API)
os.environ["SMTP_HOST"] = "smtp.gmail.com"
os.environ["SMTP_PORT"] = "587"
os.environ["SMTP_USER"] = "fofackhenri36@gmail.com"
os.environ["SMTP_PASSWORD"] = "nrcc emex nodh gfme"
os.environ["EMAILS_FROM_EMAIL"] = "fofackhenri36@gmail.com"
os.environ["EMAILS_FROM_NAME"] = "AirSentinel Alerts"

# Mock des autres settings obligatoires
os.environ["DATABASE_URL"] = "postgresql://mock"
os.environ["DATABASE_URL_SYNC"] = "postgresql://mock"
os.environ["SUPABASE_URL"] = "https://mock"
os.environ["SUPABASE_KEY"] = "mock"
os.environ["SECRET_KEY"] = "mock_secret_key_at_least_32_chars_long"

from api.services.mail_service import EmailService

async def send_to_mark():
    print("--- Envoi d'une alerte réelle à Marc Fankam ---")
    
    target_email = "marcfankam907@gmail.com"
    city = "Bafoussam"
    pm25 = 28.5
    level = "MODÉRÉ"
    color = "#FFC107"
    
    # On force l'utilisation de SMTP en bypassant Brevo pour ce test spécifique (ou on laisse le fallback faire)
    # Pour être sûr de tester Gmail, on appelle directement _send_email_smtp
    
    # Mais le template est dans send_air_quality_alert. 
    # On va modifier EmailService temporairement ou juste appeler send_air_quality_alert.
    # Si BREVO_API_KEY est absent, il fera le fallback SMTP.
    os.environ["BREVO_API_KEY"] = "" 

    await EmailService.send_air_quality_alert(
        email=target_email,
        city=city,
        pm25=pm25,
        level=level,
        color=color
    )
    print(f"✅ Commande d'envoi lancée pour {target_email}. Vérifiez les logs SMTP.")

if __name__ == "__main__":
    asyncio.run(send_to_mark())
