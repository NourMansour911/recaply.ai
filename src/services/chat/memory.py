import json
from typing import List, Dict, Optional
from integrations.redis_provider import RedisProvider

class MemoryService:
    def __init__(self, redis_provider: RedisProvider):
        self.redis = redis_provider

    def _build_session_key(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        session_id: str
    ) -> str:
        return self.redis.build_session_key(
            tenant_id, project_id, user_id, session_id
        )

    async def get_history(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        session_id: str,
    ) -> List[Dict]:

        key = self._build_session_key(
            tenant_id, project_id, user_id, session_id
        )

        history = await self.redis.get_messages(key)
        
        return history

    async def append_user_message(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        session_id: str,
        content: str
    ):
        key = self._build_session_key(
            tenant_id, project_id, user_id, session_id
        )

        await self.redis.append_message(key, {
            "role": "user",
            "content": content
        })

    async def append_ai_message(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        session_id: str,
        content: str
    ):
        key = self._build_session_key(
            tenant_id, project_id, user_id, session_id
        )

        await self.redis.append_message(key, {
            "role": "assistant",
            "content": content
        })