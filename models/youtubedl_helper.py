from time import sleep
from asyncio import get_event_loop

from discord import (
    FFmpegPCMAudio,
    PCMVolumeTransformer,
    VoiceClient,
)
from discord.ext.commands import Cog, CommandError, command
from yt_dlp import YoutubeDL

ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "",
}


ffmpeg_options = {
    "options": "-vn",
}

ytdl = YoutubeDL(ytdl_format_options)


async def auto_stop_player(duration: float, client: VoiceClient):
    sleep(duration + 1)
    if not client.is_connected():
        return
    client.stop()
    await client.disconnect()


class YTDLSource(PCMVolumeTransformer):
    def __init__(self, source, *, data: dict[str, str], volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title: str = data.get("title", "")
        self.url: str = data.get("url", "")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=False)
        )
        data: dict[str, str] = next(iter(response.get("entries", []), {}))
        filename = data.get("url", "")
        audio = FFmpegPCMAudio(filename, options="-vn")  # type ignore
        return cls(audio, data=data)  # type ignore


class YouTubeDLHelper(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    async def play(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""
        try:
            async with ctx.typing():
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                ctx.voice_client.play(
                    player, after=lambda e: print(f"Player error: {e}") if e else None
                )
            await ctx.send(f"Now playing: {player.title}")
            await auto_stop_player(player.data["duration"], ctx.voice_client)
        except Exception:
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
