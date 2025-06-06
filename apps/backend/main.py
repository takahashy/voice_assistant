# '''
# main.py

# Main entrypoint for FastAPI backend
# '''
# # Copyright 2023-2024 Deepgram SDK contributors. All Rights Reserved.
# # Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# # SPDX-License-Identifier: MIT

# import os
# import asyncio
# from time import sleep
# from dotenv import load_dotenv
# from signal import SIGINT, SIGTERM
# from deepgram.utils import verboselogs

# from deepgram import (
#     DeepgramClient,
#     DeepgramClientOptions,
#     LiveTranscriptionEvents,
#     LiveOptions,
#     Microphone,
# )

# load_dotenv()

# # We will collect the is_final=true messages here so we can use them when the person finishes speaking
# is_finals = []


# def getDeepgramAPI():
#         secret_file = os.getenv("DEEPGRAM_API_KEY_FILE")
#         password = None

#         if secret_file and os.path.exists(secret_file):
#             with open(secret_file, "r") as file:
#                 password = file.read().strip()
#         else:
#             password = os.getenv("DEEPGRAM_API_KEY")
        
#         try:
#             if not password:
#                 raise ValueError("Deepgram API key is not set.")
#         except ValueError as e:
#             print(f"Error: {e}")
#             return None
        
#         return password

# async def main():
#     try:
#         loop = asyncio.get_event_loop()

#         for signal in (SIGTERM, SIGINT):
#             loop.add_signal_handler(
#                 signal,
#                 lambda: asyncio.create_task(
#                     shutdown(signal, loop, dg_connection, microphone)
#                 ),
#             )

#         # example of setting up a client config. logging values: WARNING, VERBOSE, DEBUG, SPAM
#         config: DeepgramClientOptions = DeepgramClientOptions(
#             options={"keepalive": "true"}
#         )
#         deepgram = DeepgramClient("", config)
#         # otherwise, use default config
#         # deepgram: DeepgramClient = DeepgramClient()

#         dg_connection = deepgram.listen.asyncwebsocket.v("1")

#         async def on_open(self, open, **kwargs):
#             print("Connection Open")

#         async def on_message(self, result, **kwargs):
#             global is_finals
#             sentence = result.channel.alternatives[0].transcript
#             if len(sentence) == 0:
#                 return
#             if result.is_final:
#                 # We need to collect these and concatenate them together when we get a speech_final=true
#                 # See docs: https://developers.deepgram.com/docs/understand-endpointing-interim-results
#                 is_finals.append(sentence)

#                 # Speech Final means we have detected sufficient silence to consider this end of speech
#                 # Speech final is the lowest latency result as it triggers as soon an the endpointing value has triggered
#                 if result.speech_final:
#                     utterance = " ".join(is_finals)
#                     print(f"Speech Final: {utterance}")
#                     is_finals = []
#                 else:
#                     # These are useful if you need real time captioning and update what the Interim Results produced
#                     print(f"Is Final: {sentence}")
#             else:
#                 # These are useful if you need real time captioning of what is being spoken
#                 print(f"Interim Results: {sentence}")

#         async def on_metadata(self, metadata, **kwargs):
#             print(f"Metadata: {metadata}")

#         async def on_speech_started(self, speech_started, **kwargs):
#             print("Speech Started")

#         async def on_utterance_end(self, utterance_end, **kwargs):
#             print("Utterance End")
#             global is_finals
#             if len(is_finals) > 0:
#                 utterance = " ".join(is_finals)
#                 print(f"Utterance End: {utterance}")
#                 is_finals = []

#         async def on_close(self, close, **kwargs):
#             print("Connection Closed")

#         async def on_error(self, error, **kwargs):
#             print(f"Handled Error: {error}")

#         async def on_unhandled(self, unhandled, **kwargs):
#             print(f"Unhandled Websocket Message: {unhandled}")

#         dg_connection.on(LiveTranscriptionEvents.Open, on_open)
#         dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
#         dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
#         dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
#         dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
#         dg_connection.on(LiveTranscriptionEvents.Close, on_close)
#         dg_connection.on(LiveTranscriptionEvents.Error, on_error)
#         dg_connection.on(LiveTranscriptionEvents.Unhandled, on_unhandled)

#         # connect to websocket
#         options: LiveOptions = LiveOptions(
#             model="nova-3",
#             language="en-US",
#             # Apply smart formatting to the output
#             smart_format=True,
#             # Raw audio format deatils
#             encoding="linear16",
#             channels=1,
#             sample_rate=16000,
#             # To get UtteranceEnd, the following must be set:
#             interim_results=True,
#             utterance_end_ms="1000",
#             vad_events=True,
#             # Time in milliseconds of silence to wait for before finalizing speech
#             endpointing=300,
#         )

#         addons = {
#             # Prevent waiting for additional numbers
#             "no_delay": "true"
#         }

#         print("\n\nStart talking! Press Ctrl+C to stop...\n")
#         if await dg_connection.start(options, addons=addons) is False:
#             print("Failed to connect to Deepgram")
#             return

#         # Open a microphone stream on the default input device
#         microphone = Microphone(dg_connection.send)

#         # start microphone
#         microphone.start()

#         # wait until cancelled
#         try:
#             while True:
#                 await asyncio.sleep(1)
#         except asyncio.CancelledError:
#             # This block will be executed when the shutdown coroutine cancels all tasks
#             pass
#         finally:
#             microphone.finish()
#             await dg_connection.finish()

#         print("Finished")

#     except Exception as e:
#         print(f"Could not open socket: {e}")
#         return


# async def shutdown(signal, loop, dg_connection, microphone):
#     print(f"Received exit signal {signal.name}...")
#     microphone.finish()
#     await dg_connection.finish()
#     tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
#     [task.cancel() for task in tasks]
#     print(f"Cancelling {len(tasks)} outstanding tasks")
#     await asyncio.gather(*tasks, return_exceptions=True)
#     loop.stop()
#     print("Shutdown complete.")


# asyncio.run(main())



import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from services.deepgram import DeepgramService



# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


app = FastAPI()
manager = ConnectionManager()
deepgram = DeepgramService()

# Serve basic static frontend
app.mount("/static", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    await manager.connect(websocket)
    print("******** Client connected ********")

    def send_transcript_to_client(transcript: str):
        asyncio.create_task(manager.send_message(transcript, websocket))

    try:
        deepgram.set_callback(send_transcript_to_client)
        deepgram.initialize_connection()

        while True:
            data = await websocket.receive_bytes()
            print("*** Received audio data ***")
            print(len(data))
            deepgram.send(data)

    except WebSocketDisconnect:
            print("******** Client disconnected ********")
            manager.disconnect(websocket)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if deepgram.connection:  # Ensure connection is valid
            deepgram.connection.finish()