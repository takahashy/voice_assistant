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
is_finals = []

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

        deepgram = DeepgramClient("", config)
        self.connection = deepgram.listen.live.v("1")

        def on_open(_, open, **kwargs):
            print("-------- Deepgram connection opened. --------")

        def on_message(self, result, **kwargs):
            global is_finals
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            if result.is_final:
                # We need to collect these and concatenate them together when we get a speech_final=true
                # See docs: https://developers.deepgram.com/docs/understand-endpointing-interim-results
                is_finals.append(sentence)

                # Speech Final means we have detected sufficient silence to consider this end of speech
                # Speech final is the lowest latency result as it triggers as soon an the endpointing value has triggered
                if result.speech_final:
                    utterance = " ".join(is_finals)
                    print(f"Speech Final: {utterance}")
                    self.callback(utterance)
                    is_finals = []
                else:
                    # These are useful if you need real time captioning and update what the Interim Results produced
                    print(f"Is Final: {sentence}")
            else:
                # These are useful if you need real time captioning of what is being spoken
                print(f"Interim Results: {sentence}")


        def on_speech_started(self, speech_started, **kwargs):
            print("Speech Started")

        def on_utterance_end(self, utterance_end, **kwargs):
            print("Utterance End")
            global is_finals
            if len(is_finals) > 0:
                utterance = " ".join(is_finals)
                print(f"Utterance End: {utterance}")
                is_finals = []

        # def on_message(_, result, **kwargs):
        #     print("------- DEEPGRAM RESULT -------")
        #     print(result)
        #     transcript = result.channel.alternatives[0].transcript
        #     print(transcript)
        #     if transcript and self.callback:
        #         self.callback(transcript)

        def on_close(_, close, **kwargs):
            print("-------- Deepgram connection closed. --------")

        def on_error(_, error, **kwargs):
            print("Deepgram error:", error)

        self.connection.on(LiveTranscriptionEvents.Open, on_open)
        self.connection.on(LiveTranscriptionEvents.Transcript, on_message)
        self.connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        self.connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
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
            print("--- Sending audio data ---")
            self.connection.send(audio_data)
        else:
            print("Connection not initialized. Please call initialize_connection() first.")


    def close(self):
        if self.connection:
            self.connection.close()