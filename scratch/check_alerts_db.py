import sys
import os
import asyncio
sys.path.append(os.getcwd())

# Mock settings
os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.sbzjiekwrafzkscnrheu:XJ%40JRupSmYfrj4L@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
os.environ["DATABASE_URL_SYNC"] = "postgresql://postgres.sbzjiekwrafzkscnrheu:XJ%40JRupSmYfrj4L@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
os.environ["SUPABASE_URL"] = "https://sbzjiekwrafzkscnrheu.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNiemppZWt3cmFmemtzY25yaGV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ5MDA0MDUsImV4cCI6MjA5MDQ3NjQwNX0.N8ZFaKL7fR0-_y4ws1Cj1-RKtnX341dooJbfB67P1VQ"
os.environ["SECRET_KEY"] = "2c00bdfe30ae1167ace2edf6eb610dd678111d955c856613ea9de858320ca5c8"

from sqlalchemy import select
from api.core.database import AsyncSessionLocal
from api.models.user import User

async def check_alerts():
    async with AsyncSessionLocal() as db:
        stmt = select(User).where(User.last_alert_sent.isnot(None))
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        print(f"Nombre d'utilisateurs ayant reçu au moins une alerte : {len(users)}")
        for user in users:
            print(f"User: {user.email}, Ville: {user.subscribed_city}, Dernière alerte: {user.last_alert_sent}")

if __name__ == "__main__":
    # Mock settings for DB connection (already in config.py, but we need env vars)
    # The user provided the DB URL in render.yaml
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://postgres.sbzjiekwrafzkscnrheu:XJ%40JRupSmYfrj4L@aws-1-eu-west-1.pooler.supabase.com:6543/postgres"
    os.environ["DATABASE_URL_SYNC"] = "postgresql://postgres.sbzjiekwrafzkscnrheu:XJ%40JRupSmYfrj4L@aws-1-eu-west-1.pooler.supabase.com:5432/postgres"
    os.environ["SUPABASE_URL"] = "https://sbzjiekwrafzkscnrheu.supabase.co"
    os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNiemppZWt3cmFmemtzY25yaGV1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQ5MDA0MDUsImV4cCI6MjA5MDQ3NjQwNX0.N8ZFaKL7fR0-_y4ws1Cj1-RKtnX341dooJbfB67P1VQ"
    os.environ["SECRET_KEY"] = "2c00bdfe30ae1167ace2edf6eb610dd678111d955c856613ea9de858320ca5c8"
    
    asyncio.run(check_alerts())
