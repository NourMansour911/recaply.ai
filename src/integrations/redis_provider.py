import redis.asyncio as redis
from typing import Optional, List, Dict, Any
import hashlib
from helpers.logger import get_logger

logger = get_logger(__name__)


class RedisProvider:
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        password: Optional[str] = None,

    ):
        self.host = host
        self.port = port
        self.password = password

        self.client: Optional[redis.Redis] = None


    async def connect(self) -> None:
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                decode_responses=True
            )
            logger.info("[REDIS CONNECT SUCCESS]")
        except Exception as e:
            logger.error(f"[REDIS ERROR] {e}")
            raise

    async def disconnect(self) -> None:
        if self.client:
            await self.client.close()
            self.client = None
        logger.info("[REDIS DISCONNECT]")


    async def ping(self) -> bool:
        return await self.client.ping()



    def build_key(
        self,
        tenant_id: str,
        project_id: str,
        key_type: str,
        identifier: str
    ) -> str:
        return f"tenant:{tenant_id}:project:{project_id}:{key_type}:{identifier}"

    def hash_value(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()



    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl: int = 300
    ) -> None:
        await self.client.set(key, value, ex=ttl)

    async def delete(self, key: str) -> None:
        await self.client.delete(key)


    async def hset(
        self,
        key: str,
        mapping: Dict[str, Any]
    ) -> None:
        await self.client.hset(key, mapping=mapping)

    async def hgetall(self, key: str) -> Dict[str, Any]:
        return await self.client.hgetall(key)


    async def push(self, key: str, value: str) -> None:
        await self.client.rpush(key, value)

    async def pop(self, key: str) -> Optional[str]:
        return await self.client.lpop(key)

    async def get_list(self, key: str) -> List[str]:
        return await self.client.lrange(key, 0, -1)

    async def add_to_set(self, key: str, value: str) -> None:
        await self.client.sadd(key, value)

    async def get_set(self, key: str) -> List[str]:
        return list(await self.client.smembers(key))


    def build_session_key(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        session_id: str
    ) -> str:
        return f"tenant:{tenant_id}:project:{project_id}:user:{user_id}:session:{session_id}"

    async def append_message(
        self,
        key: str,
        message: str
    ) -> None:
        await self.push(key, message)

    async def get_messages(
        self,
        key: str
    ) -> List[str]:
        return await self.get_list(key)



    def build_cache_key(
        self,
        tenant_id: str,
        project_id: str,
        prompt: str
    ) -> str:
        h = self.hash_value(prompt)
        return f"tenant:{tenant_id}:project:{project_id}:cache:{h}"

    async def get_cache(self, key: str) -> Optional[str]:
        return await self.get(key)

    async def set_cache(
        self,
        key: str,
        value: str,
        ttl: int = 300
    ) -> None:
        await self.set(key, value, ttl=ttl)