import discord
from discord.ext import commands
import redis.asyncio as redis
from config.settings import REDIS_URI

class EquinoxBot(commands.Bot):
    def __init__(self, bot_name: str, command_prefix: str, theme_color: int, persona: str):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True

        super().__init__(command_prefix=command_prefix, intents=intents)

        self.bot_name = bot_name
        self.theme_color = theme_color
        self.persona = persona
        self.redis = None
        self.pubsub = None

    async def setup_hook(self):
        self.redis = redis.from_url(REDIS_URI, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        await self.pubsub.subscribe("equinox_system")
        self.loop.create_task(self.pubsub_listener())

    async def pubsub_listener(self):
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                self.dispatch("system_event", message["data"])

    async def load_module_cogs(self, extensions: list):
        for ext in extensions:
            await self.load_extension(ext)

    async def close(self):
        if self.pubsub:
            await self.pubsub.unsubscribe("equinox_system")
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
        await super().close()

    async def on_ready(self):
        print(f"[{self.bot_name}] Identity Loaded: {self.user.name} | Prefix: {self.command_prefix}")
