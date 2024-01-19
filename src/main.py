from asyncio import run
from os import getenv

from discord import ClientUser, Intents
from discord.ext.commands import Bot, when_mentioned_or

from models.youtubedl_helper import YouTubeDLHelper

intents = Intents.default()
intents.message_content = True

bot = Bot(
    command_prefix=when_mentioned_or("!"),
    description="Relatively simple music bot example",
    intents=intents,
)


@bot.event
async def on_ready():
    user: ClientUser = bot.user  # type: ignore
    print(f"Logged in as {user} (ID: {user.id})")
    print("------")


async def main():
    async with bot:
        await bot.add_cog(YouTubeDLHelper(bot))
        await bot.start(getenv("API_TOKEN", ""))


run(main())
