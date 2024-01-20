from time import sleep
from asyncio import get_event_loop

from discord import (
    FFmpegPCMAudio,
    PCMVolumeTransformer,
    VoiceClient,
)
from yt_dlp import YoutubeDL

DEFAULT_PARAMS = {
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


async def auto_stop_player(duration: float, client: VoiceClient):
    sleep(duration + 1)
    if not client.is_connected():
        return
    client.stop()
    await client.disconnect()


class YouTubeDLHelper(PCMVolumeTransformer):
    def __init__(self, source, *, data: dict[str, str], volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title: str = data.get("title", "")
        self.url: str = data.get("url", "")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: YoutubeDL(DEFAULT_PARAMS).extract_info(url, download=False),
        )
        data: dict[str, str] = (
            response.get("entries", [])[0] if "entries" in response else response
        )
        filename = data.get("url", "")
        # options: str = "-vn -ss 7 -t 3"
        audio = FFmpegPCMAudio(filename, options="-vn")  # type ignore
        return cls(audio, data=data)  # type ignore
