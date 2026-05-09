import asyncio
import sys
from pathlib import Path

# Ajouter la racine du projet au path pour importer api
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from api.services.mail_service import EmailService
from api.core.config import settings

async def test_alert():
    print(f"--- Test d'envoi d'email via BREVO ---")
    print(f"Brevo API Key: {'Configurée' if settings.BREVO_API_KEY else 'NON TROUVÉE'}")
    print(f"Sender: {settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>")
    
    if not settings.BREVO_API_KEY:
        print("ERROR: BREVO_API_KEY est manquante dans le fichier api/.env")
        return

    test_email = settings.EMAILS_FROM_EMAIL # On s'envoie le mail à soi-même pour tester
    
    try:
        await EmailService.send_air_quality_alert(
            email=test_email,
            city="Douala (Test Brevo API)",
            pm25=45.5,
            level="MAUVAIS",
            color="#FF5722"
        )
        print(f"\nSUCCESS ! La requête a été envoyée à Brevo pour {test_email}")
        print("Veuillez vérifier votre boîte de réception (et vos spams).")
    except Exception as e:
        print(f"FAILURE : {e}")

if __name__ == "__main__":
    asyncio.run(test_alert())
