from discord.ext.commands import Cog, CommandError, command
from zurkon.models.youtubedl_helper import YouTubeDLHelper, auto_stop_player


class ZurkonController(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def play(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        try:
            async with ctx.typing():
                print("foo")
                player = await YouTubeDLHelper.from_url(url, loop=self.bot.loop)
                print(player)
                ctx.voice_client.play(
                    player, after=lambda e: print(f"Player error: {e}") if e else None
                )
            await ctx.send(f"Now playing: {player.title}")
            await auto_stop_player(player.data["duration"], ctx.voice_client)
        except Exception as e:
            print(e)
            if ctx.voice_client is not None:
                await ctx.voice_client.disconnect()

    @command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""

        if ctx.voice_client is None:
            return await ctx.send("Not connected to a voice channel.")

        ctx.voice_client.source.volume = volume / 100
        await ctx.send(f"Changed volume to {volume}%")

    @command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()
