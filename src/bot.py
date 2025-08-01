import discord
import requests
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID")
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_subs_count = None  # Para controlar mudanças e evitar spam

    async def setup_hook(self):
        self.bg_task = asyncio.create_task(self.update_subscriber_count())

    async def update_subscriber_count(self):
        await self.wait_until_ready()
        channel = self.get_channel(DISCORD_CHANNEL_ID)
        if channel is None:
            print("[ERROR] Channel not found")
            return

        while not self.is_closed():
            try:
                url = (
                    f"https://www.googleapis.com/youtube/v3/channels?"
                    f"part=statistics&id={YOUTUBE_CHANNEL_ID}&key={YOUTUBE_API_KEY}"
                )
                response = requests.get(url).json()
                subs = response['items'][0]['statistics']['subscriberCount']

                if subs != self.last_subs_count:
                    await channel.send(f"📢 Current subscribers: {subs}")
                    print(f"[INFO] Sent subscriber count: {subs}")
                    self.last_subs_count = subs

            except Exception as e:
                print(f"[ERROR] {e}")

            await asyncio.sleep(7200)

    async def on_ready(self):
        print(f'✅ Logged in as {self.user} ({self.user.id})')

intents = discord.Intents.default()
client = MyClient(intents=intents)

client.run(DISCORD_TOKEN)