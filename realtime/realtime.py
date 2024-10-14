import asyncio
import websockets
import json
import base64
import uuid
import threading
import sys
from typing import List, Dict, Any
import pyaudio

# Constants
WEBSOCKET_URI = "wss://api.openai.com/v1/assistants-streaming"
MODEL = "gpt-4o-realtime-preview-2024-10-01"
MODALITIES = ["text", "audio"]
VOICE = "alloy"
TRANSCRIPTION_MODEL = "whisper-1"
AUDIO_FORMAT = "pcm16"
TURN_DETECTION = {
    "type": "server_vad",
    "threshold": 0.5
}
SILENCE_DURATION_MS = 200

# Initialize PyAudio for audio playback
p = pyaudio.PyAudio()

def play_audio(audio_bytes: bytes):
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    output=True)
    stream.write(audio_bytes)
    stream.stop_stream()
    stream.close()

class Client:
    def __init__(self):
        self.websocket = None
        self.session_id = None
        self.input_audio_buffer = bytearray()
        self.conversation: List[Dict[str, Any]] = []
        self.running = True
        self.lock = threading.Lock()

    async def connect(self):
        try:
            async with websockets.connect(WEBSOCKET_URI) as ws:
                self.websocket = ws
                await self.create_session()
                await asyncio.gather(
                    self.receive(),
                    self.handle_user_input()
                )
        except Exception as e:
            print(f"Error occurred: {e}")

    async def create_session(self):
        session_message = {
            "action": "create_session",
            "model": MODEL,
            "modalities": MODALITIES,
            "voice": VOICE,
            "input_audio_transcription": {
                "model": TRANSCRIPTION_MODEL,
                "format": AUDIO_FORMAT
            },
            "output_audio_format": AUDIO_FORMAT,
            "turn_detection": TURN_DETECTION,
            "silence_duration_ms": SILENCE_DURATION_MS
        }
        await self.websocket.send(json.dumps(session_message))
        print("Session creation message sent.")

    async def handle_user_input(self):
        loop = asyncio.get_event_loop()
        while self.running:
            user_input = await loop.run_in_executor(None, sys.stdin.readline)
            user_input = user_input.strip()
            if user_input.lower() == "/exit":
                await self.close_connection()
                break
            elif user_input.startswith("/truncate "):
                item_id = user_input.split(" ", 1)[1]
                await self.truncate_item(item_id)
            elif user_input.startswith("/delete "):
                item_id = user_input.split(" ", 1)[1]
                await self.delete_item(item_id)
            elif user_input.startswith("/audio "):
                # Assume audio input is provided as a file path
                file_path = user_input.split(" ", 1)[1]
                await self.handle_audio_input(file_path)
            else:
                await self.send_text_message(user_input)

    async def send_text_message(self, text: str):
        message = {
            "action": "send_conversation_item",
            "type": "text",
            "content": text,
            "id": str(uuid.uuid4())
        }
        self.conversation.append(message)
        await self.websocket.send(json.dumps(message))
        print(f"User said: {text}")

    async def handle_audio_input(self, file_path: str):
        try:
            with open(file_path, "rb") as f:
                audio_data = f.read()
                encoded_audio = base64.b64encode(audio_data).decode('utf-8')
                message = {
                    "action": "send_conversation_item",
                    "type": "audio",
                    "content": encoded_audio,
                    "id": str(uuid.uuid4())
                }
                self.conversation.append(message)
                await self.websocket.send(json.dumps(message))
                print("Audio message sent to the server.")
        except Exception as e:
            print(f"Failed to send audio message: {e}")

    async def truncate_item(self, item_id: str):
        message = {
            "action": "truncate_item",
            "id": item_id
        }
        await self.websocket.send(json.dumps(message))
        print(f"Truncated item {item_id}")

    async def delete_item(self, item_id: str):
        message = {
            "action": "delete_item",
            "id": item_id
        }
        await self.websocket.send(json.dumps(message))
        print(f"Deleted item {item_id}")

    async def receive(self):
        try:
            async for message in self.websocket:
                await self.handle_response(message)
        except websockets.exceptions.ConnectionClosed:
            print("Connection closed by server.")
        except Exception as e:
            print(f"Error occurred: {e}")

    async def handle_response(self, message: str):
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            if msg_type == "session_created":
                self.session_id = data.get("session_id")
                print("Session created successfully.")
            elif msg_type == "text":
                text = data.get("content")
                print(f"Assistant: {text}")
            elif msg_type == "audio":
                encoded_audio = data.get("content")
                audio_bytes = base64.b64decode(encoded_audio)
                threading.Thread(target=play_audio, args=(audio_bytes,)).start()
            elif msg_type == "function_call":
                function_name = data.get("function_name")
                parameters = data.get("parameters")
                print(f"Calling function {function_name} with parameters: {parameters}")
            elif msg_type == "error":
                error_message = data.get("message")
                print(f"Error: {error_message}")
            else:
                print(f"Unknown message type: {msg_type}")
        except json.JSONDecodeError:
            print("Received non-JSON message.")
        except Exception as e:
            print(f"Failed to handle response: {e}")

    async def close_connection(self):
        self.running = False
        if self.websocket:
            await self.websocket.close()
            print("Connection closed.")

def main():
    client = Client()
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(client.connect())
    except KeyboardInterrupt:
        print("Interrupted by user.")
        loop.run_until_complete(client.close_connection())
    finally:
        p.terminate()
        loop.close()

if __name__ == "__main__":
    print("Starting client. Type '/exit' to quit.")
    print("Commands:")
    print("  /exit - Close the connection and exit.")
    print("  /truncate <item_id> - Truncate a conversation item.")
    print("  /delete <item_id> - Delete a conversation item.")
    print("  /audio <file_path> - Send an audio file as input.")
    main()
