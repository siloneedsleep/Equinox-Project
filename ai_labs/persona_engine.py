import time
import json
from google import genai
from google.genai import types

class AIEngine:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.personas = {
            "Luminous": "Ngươi là Nữ thần Luminous, đại diện cho ánh sáng, văn minh và hoàng gia. Trả lời thanh lịch, thông thái, mang tính chữa lành.",
            "Tenebris": "Ngươi là Chúa tể Tenebris, đại diện cho thế giới ngầm, chợ đen. Trả lời cục súc, giang hồ, mỉa mai, có tính lừa lọc để tạo drama."
        }

    async def _get_active_key(self):
        keys = await self.redis.hgetall("api_keys")
        current_time = int(time.time())
        
        for token_id, data_str in keys.items():
            data = json.loads(data_str)
            if data["status"] == "active":
                return token_id, data["key_content"]
            elif data["status"] == "cooldown" and current_time >= data.get("cooldown_until", 0):
                data["status"] = "active"
                await self.redis.hset("api_keys", token_id, json.dumps(data))
                return token_id, data["key_content"]
        return None, None

    async def _handle_api_error(self, token_id: str, error_code: int):
        raw_data = await self.redis.hget("api_keys", token_id)
        if not raw_data: return
        
        data = json.loads(raw_data)
        if error_code == 429:
            data["status"] = "cooldown"
            data["cooldown_until"] = int(time.time()) + 300
        elif error_code in [401, 403]:
            data["status"] = "banned"
            
        await self.redis.hset("api_keys", token_id, json.dumps(data))

    async def generate_response(self, user_id: int, user_message: str, persona: str) -> str:
        token_id, api_key = await self._get_active_key()
        if not api_key:
            return "Hệ thống AI hiện đang quá tải hoặc hết năng lượng. Vui lòng thử lại sau."

        client = genai.Client(api_key=api_key)
        system_instruction = self.personas.get(persona, "")
        history_key = f"chat_history:{user_id}"
        history = await self.redis.lrange(history_key, 0, -1)
        
        contents = []
        for msg in history[-10:]:
            role, text = msg.split("::", 1)
            contents.append(types.Content(role=role, parts=[types.Part.from_text(text=text)]))
            
        contents.append(types.Content(role="user", parts=[types.Part.from_text(text=user_message)]))

        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7
                )
            )
            reply_text = response.text
            
            await self.redis.rpush(history_key, f"user::{user_message}")
            await self.redis.rpush(history_key, f"model::{reply_text}")
            await self.redis.ltrim(history_key, -10, -1)
            
            return reply_text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                await self._handle_api_error(token_id, 429)
                return await self.generate_response(user_id, user_message, persona)
            elif "401" in error_str or "403" in error_str:
                await self._handle_api_error(token_id, 401)
                return await self.generate_response(user_id, user_message, persona)
            return "Có lỗi gián đoạn không gian mạng, ta không thể hồi đáp lúc này."
