












# app/main.py
import os
import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from services.deepgram import DeepgramService

# FastAPI App
app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

websockets = []  # Track connected WebSocket clients

# Initialize Deepgram handler with no callback initially
dg_handler = DeepgramService()

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websockets.append(websocket)
    print("Client connected.")

    # Define how to handle received transcripts
    def send_transcript_to_client(transcript: str):
        try:
            for ws in websockets:
                if not ws.client_state.name == "DISCONNECTED":
                    asyncio.create_task(ws.send_json({"transcription": transcript}))
        except Exception as e:
            print("Send transcript error:", e)

    # Assign the callback and start the Deepgram connection
    dg_handler.set_callback(send_transcript_to_client)
    dg_handler.initialize_connection()

    try:
        while True:
            data = await websocket.receive_bytes()
            if dg_handler.dg_connection:
                dg_handler.dg_connection.send(data)

    except WebSocketDisconnect:
        print("Client disconnected")
        websockets.remove(websocket)
        if dg_handler.dg_connection:
            dg_handler.dg_connection.finish()


