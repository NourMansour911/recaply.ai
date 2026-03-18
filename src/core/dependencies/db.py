from fastapi import Request
from motor.motor_asyncio import AsyncIOMotorClient
def get_db_client(request: Request) -> AsyncIOMotorClient :
        return request.app.db_client