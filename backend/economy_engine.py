import random
import time
import json

class EconomyEngine:
    def __init__(self, db):
        self.db = db

    async def open_star_pouch(self, user_id: int, current_persona: str) -> dict:
        amount = random.randint(100, 10000000)
        currency_type = "aequor" if current_persona == "Luminous" else "aequis"
        
        await self.db.update_currency(user_id, currency_type, amount)
        
        return {
            "amount": amount,
            "currency": currency_type,
            "persona": current_persona
        }

    async def launder_money(self, user_id: int, amount: int) -> dict:
        current_dirty = await self.db.redis.hget(f"user:{user_id}:economy", "aequis")
        current_dirty = int(current_dirty) if current_dirty else 0

        if current_dirty < amount:
            return {"success": False, "reason": "Số dư Aequis không đủ."}

        fee_percent = random.randint(15, 25)
        fee_amount = int(amount * (fee_percent / 100))
        clean_amount = amount - fee_amount

        await self.db.update_currency(user_id, "aequis", -amount)
        await self.db.update_currency(user_id, "aequor", clean_amount)
        await self.db.update_currency("system_family_fund", "aequor", fee_amount)

        return {
            "success": True,
            "clean_received": clean_amount,
            "fee_paid": fee_amount,
            "fee_percent": fee_percent
        }

    async def create_trade_session(self, user1_id: int, user2_id: int) -> str:
        session_id = f"trade:{user1_id}:{user2_id}:{int(time.time())}"
        payload = {
            "user1": {"id": user1_id, "offer": {"aequor": 0, "aequis": 0, "items": []}, "confirmed": False},
            "user2": {"id": user2_id, "offer": {"aequor": 0, "aequis": 0, "items": []}, "confirmed": False},
            "status": "pending"
        }
        await self.db.redis.setex(session_id, 300, json.dumps(payload))
        return session_id
