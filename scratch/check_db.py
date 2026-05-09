
import asyncio
import os
from dotenv import load_dotenv

# Load env before importing other stuff
load_dotenv("api/.env")

from sqlalchemy import select, func
from api.core.database import AsyncSessionLocal
from api.models.user import User

async def check_users():
    async with AsyncSessionLocal() as db:
        total_users_stmt = select(func.count(User.id))
        total_users = (await db.execute(total_users_stmt)).scalar()
        
        users_with_token_stmt = select(func.count(User.id)).where(User.fcm_token.isnot(None))
        users_with_token = (await db.execute(users_with_token_stmt)).scalar()
        
        print(f"Total users: {total_users}")
        print(f"Users with FCM token: {users_with_token}")
        
        if users_with_token > 0:
            stmt = select(User).where(User.fcm_token.isnot(None))
            result = await db.execute(stmt)
            users = result.scalars().all()
            for u in users:
                print(f"User: {u.email}, Token: {u.fcm_token[:20]}...")
        else:
            print("No users with FCM token found.")

if __name__ == "__main__":
    asyncio.run(check_users())
