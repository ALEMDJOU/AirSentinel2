import asyncio
import sys
from pathlib import Path
from sqlalchemy import select

# Ajouter la racine du projet au path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from api.core.database import AsyncSessionLocal
from api.models.user import User
from api.services.mail_service import EmailService

async def broadcast_emails():
    print("\n" + "="*50)
    print("STARTING AIRSENTINEL BROADCAST")
    print("="*50 + "\n")
    
    async with AsyncSessionLocal() as db:
        # Récupérer tous les utilisateurs actifs
        stmt = select(User).where(User.is_active == True)
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        if not users:
            print("No user found in database.")
            return
            
        print(f"Number of users to contact : {len(users)}")
        print("-" * 30)
        
        subject = "AirSentinel : Votre systeme d'alerte est pret !"
        message = """
        Nous sommes ravis de vous annoncer que le système d'alerte AirSentinel est désormais pleinement opérationnel. 
        <br><br>
        Grâce à notre nouvelle intégration avec <b>Brevo</b>, vous recevrez désormais des alertes ultra-rapides et fiables dès que la qualité de l'air se dégrade dans votre ville abonnée.
        <br><br>
        N'oubliez pas de configurer votre ville dans votre profil pour recevoir des notifications personnalisées.
        """
        
        count = 0
        for user in users:
            try:
                print(f"Sending to {user.email}...", end=" ", flush=True)
                await EmailService.send_broadcast_message(
                    email=user.email,
                    name=user.full_name,
                    subject=subject,
                    message=message
                )
                print("OK")
                count += 1
                # Petit délai pour éviter de saturer l'API Brevo (même si elle encaisse bien)
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"Error : {e}")
                
        print("\n" + "="*50)
        print(f"BROADCAST FINISHED : {count}/{len(users)} sent")
        print("="*50 + "\n")

if __name__ == "__main__":
    asyncio.run(broadcast_emails())
