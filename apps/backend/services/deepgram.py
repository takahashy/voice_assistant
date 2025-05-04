'''
deepgram.py

Use Deepgram API to detect and transcribe live audio. Speach to text
'''
import os
import logging
from dotenv import load_dotenv
from deepgram import (
    DeepgramClient, 
    LiveTranscriptionEvents, 
    LiveOptions, 
    DeepgramClientOptions
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(SCRIPT_DIR, "../../../.env")

load_dotenv(ENV_PATH)

# Service class to handle Deepgram API interactions
class DeepgramService:
    def __init__(self):
        self.connection = None
        self.callback = None


    def __getDeepgramAPI(self):
        secret_file = os.getenv("DEEPGRAM_API_KEY_FILE")
        password = None

        if secret_file and os.path.exists(secret_file):
            with open(secret_file, "r") as file:
                password = file.read().strip()
        else:
            password = os.getenv("DEEPGRAM_API_KEY")
        
        try:
            if not password:
                raise ValueError("Deepgram API key is not set.")
        except ValueError as e:
            print(f"Error: {e}")
            return None
        
        return password
    

    def set_callback(self, callback):
        self.callback = callback
    

    def initialize_connection(self):
        deepgram_api_key = self.__getDeepgramAPI()
        
        config = DeepgramClientOptions(
            verbose=logging.INFO,
            options={"keep_alive": "true"}
        )

        deepgram = DeepgramClient(deepgram_api_key, config)
        self.connection = deepgram.client.listen.live.v("1")

        def on_open(_, open, **kwargs):
            print("Deepgram connection opened.")

        def on_message(_, result, **kwargs):
            transcript = result.channel.alternatives[0].transcript
            if transcript and self.callback:
                self.callback(transcript)

        def on_close(_, close, **kwargs):
            print("Deepgram connection closed.")

        def on_error(_, error, **kwargs):
            print("Deepgram error:", error)

        self.connection.on(LiveTranscriptionEvents.Open, on_open)
        self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
        self.connection.on(LiveTranscriptionEvents.Close, on_close)
        self.connection.on(LiveTranscriptionEvents.Error, on_error)

        options = LiveOptions(
            model="nova-3",
            language="en-US",
            interim_results=True,
            utterance_end_ms="1000",
            vad_events=True,
            endpointing=500
        )

        try:
            if not self.connection.start(options):
                raise RuntimeError("Failed to start Deepgram connection.")
        except RuntimeError as e:
            print(f"Error: {e}")
            

    def send(self, audio_data):
        if self.connection:
            self.connection.send(audio_data)
        else:
            print("Connection not initialized. Please call initialize_connection() first.")


    def close(self):
        if self.connection:
            self.connection.close()