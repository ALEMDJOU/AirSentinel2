# api/migrate.py

import os
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

async def migrate():
    if not DATABASE_URL:
        print("ERROR : DATABASE_URL non trouvee dans .env")
        return

    print("Connexion a la base de donnees...")
    engine = create_async_engine(DATABASE_URL)

    async with engine.begin() as conn:
        print("--- Ajout des colonnes manquantes a la table 'users' ---")
        
        # SQL pour ajouter les colonnes si elles n'existent pas
        sql_commands = [
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS subscribed_city VARCHAR(100);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS last_alert_sent TIMESTAMP WITH TIME ZONE;",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS fcm_token VARCHAR(255);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_alerts_enabled BOOLEAN DEFAULT TRUE;"
        ]
        
        for sql in sql_commands:
            try:
                await conn.execute(text(sql))
                print(f"OK : {sql}")
            except Exception as e:
                print(f"ERROR : {sql}: {e}")

    await engine.dispose()
    print("DONE : Migration terminee !")

if __name__ == "__main__":
    asyncio.run(migrate())
