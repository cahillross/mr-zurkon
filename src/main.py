from asyncio import run
from os import getenv

from discord import ClientUser, Intents
from discord.ext.commands import Bot, when_mentioned_or

from zurkon.models.zurkon_controller import ZurkonController

intents = Intents.default()
intents.message_content = True

bot = Bot(
    command_prefix=when_mentioned_or("!"),
    description="Relatively simple music bot example",
    intents=intents,
)


@bot.event
async def on_ready():
    """Event handler for when the bot has established a connection to Discord."""
    user: ClientUser = bot.user  # type: ignore
    print(f"Logged in as {user} (ID: {user.id})")
    print("------")


async def main():
    async with bot:
        await bot.add_cog(ZurkonController(bot))
        await bot.start(getenv("API_TOKEN", ""))


run(main())
