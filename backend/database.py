import json
import time
import uuid
from typing import Optional

class EquinoxDatabase:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def get_user_level(self, user_id: int) -> int:
        level = await self.redis.hget(f"user:{user_id}", "level")
        return int(level) if level else 0

    async def set_user_level(self, user_id: int, level: int):
        await self.redis.hset(f"user:{user_id}", "level", level)

    async def create_premium_key(self, duration_days: int) -> str:
        token = f"EQNX-VIP-{duration_days}D-{str(uuid.uuid4())[:8].upper()}"
        payload = {
            "duration": duration_days,
            "created_at": int(time.time()),
            "status": "available",
            "used_by": None
        }
        await self.redis.hset("premium_keys", token, json.dumps(payload))
        return token

    async def redeem_premium_key(self, user_id: int, token: str) -> bool:
        raw_data = await self.redis.hget("premium_keys", token)
        if not raw_data:
            return False
        
        key_data = json.loads(raw_data)
        if key_data["status"] != "available":
            return False
            
        key_data["status"] = "used"
        key_data["used_by"] = user_id
        key_data["activated_at"] = int(time.time())
        
        await self.redis.hset("premium_keys", token, json.dumps(key_data))
        
        current_expire = await self.redis.hget(f"user:{user_id}", "premium_until")
        base_time = int(current_expire) if current_expire and int(current_expire) > time.time() else int(time.time())
        new_expire = base_time + (key_data["duration"] * 86400)
        
        await self.redis.hset(f"user:{user_id}", "premium_until", new_expire)
        return True

    async def has_premium(self, user_id: int) -> bool:
        expire_time = await self.redis.hget(f"user:{user_id}", "premium_until")
        if not expire_time:
            return False
        return int(time.time()) < int(expire_time)

    async def save_custom_status(self, user_id: int, status_payload: dict):
        await self.redis.hset("custom_statuses", str(user_id), json.dumps(status_payload))

    async def get_custom_status(self, user_id: int) -> Optional[dict]:
        data = await self.redis.hget("custom_statuses", str(user_id))
        return json.loads(data) if data else None

    async def toggle_livestatus(self, user_id: int, state: bool):
        if state:
            await self.redis.set(f"livestatus:active:{user_id}", "1")
        else:
            await self.redis.delete(f"livestatus:active:{user_id}")

    async def add_item_to_bag(self, user_id: int, item_type: str, item_data: dict):
        item_id = str(uuid.uuid4())
        payload = {
            "id": item_id,
            "type": item_type,
            "data": item_data,
            "acquired_at": int(time.time())
        }
        await self.redis.hset(f"bag:{user_id}", item_id, json.dumps(payload))

    async def update_currency(self, user_id: int, currency_type: str, amount: int) -> int:
        return await self.redis.hincrby(f"user:{user_id}:economy", currency_type, amount)
