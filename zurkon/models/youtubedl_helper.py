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


def get_options(start: int, duration: int) -> str:
    """Set options for ffmpeg, including start of video and duration.

    Args:
        start (int): start of video in seconds
        duration (int): duration of video in seconds

    Returns:
        str: ffmpeg options
    """
    if duration >= 20:
        duration = 20
    options: str = "-vn"
    if start > 0:
        options += f" -ss {start}"
    if duration > 0:
        options += f" -t {duration}"
    return options


async def auto_stop_player(duration: float, client: VoiceClient):
    """Automatically stop player after duration.

    Args:
        duration (float): delay in seconds
        client (VoiceClient): Bot client
    """
    sleep(duration + 2)
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
    async def from_url(cls, url, *, loop=None, stream=False, start: int = 0, duration: int = 20):
        loop = loop or get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: YoutubeDL(DEFAULT_PARAMS).extract_info(url, download=False),
        )
        data: dict = (
            response.get("entries", [])[0] if "entries" in response else response
        )
        filename: str = data.get("url", "")
        duration: float = data.get("duration", 0) if duration > data.get("duration", 0) else duration
        options: str = get_options(start, duration)
        audio = FFmpegPCMAudio(filename, options=options)  # type ignore
        return cls(audio, data=data)  # type ignore
