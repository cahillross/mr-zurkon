from discord.ext.commands import Cog, CommandError, command, Context
from zurkon.models.youtubedl_helper import YouTubeDLHelper, auto_stop_player


class ZurkonController(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def play(self, ctx: Context, *, url: str):
        """Streams from a url (same as yt, but doesn't predownload)"""
        try:
            async with ctx.typing():
                player = await YouTubeDLHelper.from_url(url, loop=self.bot.loop)
                ctx.voice_client.play(
                    player, after=lambda e: print(f"Player error: {e}") if e else None
                )
            await ctx.send(f"Now playing: {player.title}")
            duration: float = player.data["duration"] if player.data["duration"] < 20 else 20
            await auto_stop_player(duration, ctx.voice_client)
        except Exception as e:
            print(e)
            if ctx.voice_client is not None:
                await ctx.voice_client.disconnect()

    @command()
    async def volume(self, ctx: Context, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @command()
    async def stop(self, ctx: Context):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx: Context):
        voice_client = ctx.voice_client
        author_voice = ctx.author.voice

        if not author_voice:
            await ctx.send("You are not connected to a voice channel.")
            raise CommandError("Author not connected to a voice channel.")
        if voice_client is None:
            await author_voice.channel.connect()
        elif voice_client.is_playing():
            voice_client.stop()
