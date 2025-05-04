import os
import asyncio
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv("../../.env")
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

if not DEEPGRAM_API_KEY:
    raise ValueError("DEEPGRAM_API_KEY is not set in the environment variables.")

class DeepgramService:
    def __init__(self):
        self.client = DeepgramClient(DEEPGRAM_API_KEY)

    async def transcribe_audio(self, audio_url: str) -> str:
        response = await self.client.transcription.sync_prerecorded(
            audio_url,
            {
                "punctuate": True,
                "language": "en-US",
                "model": "general",
                "tier": "nxt",
            },
        )
        return response["channel"]["alternatives"][0]["transcript"]