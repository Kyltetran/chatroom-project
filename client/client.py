import socket
import threading
import asyncio
import websockets
import json
import time
from datetime import datetime

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.encrypt import encrypt_message, decrypt_message
from shared.common import build_message, parse_message
from shared.config import SERVER_IP, SERVER_PORT, BUFFER_SIZE

EMOJI_MAP = {
    ":smile:": "😄",
    ":heart:": "❤️",
    ":laugh:": "😂",
    ":sad:": "😢",
    ":thumbsup:": "👍",
    ":fire:": "🔥",
}

message_queue = None  # We will initialize it later
username_global = None
client_socket_global = None
loop_global = None    # Store event loop globally so we can reference it

def apply_emoji(text):
    for code, emoji in EMOJI_MAP.items():
        text = text.replace(code, emoji)
    return text

async def websocket_handler(websocket, path):
    global username_global, client_socket_global

    print("[WEBSOCKET] React UI connected")

    # Wait for username init
    init_data = await websocket.recv()
    try:
        init_msg = json.loads(init_data)
        if init_msg.get("type") == "init":
            username_global = init_msg["username"].strip()
            if not username_global:
                await websocket.send(json.dumps({
                    "type": "system",
                    "user": "System",
                    "text": "Username cannot be empty.",
                    "timestamp": current_timestamp(),
                    "system": True
                }))
                return

            print(f"[INIT] Username received from React: {username_global}")
        else:
            await websocket.send(json.dumps({
                "type": "system",
                "user": "System",
                "text": "Expected init message.",
                "timestamp": current_timestamp(),
                "system": True
            }))
            return
    except Exception as e:
        print(f"[ERROR] Invalid init message: {e}")
        return

    # Proceed to connect to server now
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"[ERROR] Could not connect to server: {e}")
        return

    client_socket_global = client

    # Send login request
    login_message = build_message("system", username_global, "login_request", timestamp=current_timestamp())
    client.send(encrypt_message(login_message))
    print(f"[SYSTEM] Connected to server as '{username_global}'")

    # Start receiving
    threading.Thread(target=receive_messages, args=(client, username_global), daemon=True).start()

    # Handle messages from React
    try:
        async for msg_text in websocket:
            msg_text = msg_text.strip()
            if not msg_text:
                continue

            text = apply_emoji(msg_text)
            timestamp = current_timestamp()

            if text.startswith("/w "):
                parts = text.split(" ", 2)
                if len(parts) < 3:
                    await websocket.send(json.dumps({
                        "type": "system",
                        "user": "System",
                        "text": "Invalid private message format. Use /w username message",
                        "timestamp": timestamp,
                        "system": True
                    }))
                    continue
                receiver, msg_content = parts[1], parts[2]
                msg = build_message("private", username_global, msg_content, receiver=receiver, timestamp=timestamp)
                print(f"(Private to {receiver}) {timestamp}: {msg_content}")
            else:
                msg = build_message("public", username_global, text, timestamp=timestamp)

            client_socket_global.send(encrypt_message(msg))

    except websockets.ConnectionClosed:
        print("[WEBSOCKET] React UI disconnected")

def forward_to_ui(msg_dict):
    asyncio.run_coroutine_threadsafe(
        message_queue.put(json.dumps(msg_dict)),
        loop_global
    )


def receive_messages(sock, username):
    while True:
        try:
            data = sock.recv(BUFFER_SIZE)
            if not data:
                print("[SYSTEM] Server closed the connection.")
                break

            decrypted = decrypt_message(data)
            msg = parse_message(decrypted)

            msg_type = msg.get("type")
            sender = msg.get("sender")
            message = apply_emoji(msg.get("message"))
            receiver = msg.get("receiver", None)
            timestamp = msg.get("timestamp", "")

            ui_msg = {
                "type": msg_type,
                "user": sender,
                "text": message,
                "timestamp": timestamp,
                "receiver": receiver,
                "system": msg_type == "system"
            }

            forward_to_ui(ui_msg)

            if msg_type == "system":
                print(f"[SYSTEM] {message}")
            elif msg_type == "public":
                print(f"(Global) {timestamp} {sender} > {message}")
            elif msg_type == "private":
                if sender == username:
                    print(f"(Private to {receiver}) {timestamp}: {message}")
                else:
                    print(f"(Private) {sender} {timestamp}: {message}")

        except Exception as e:
            print(f"[RECEIVE ERROR] {e}")
            break

def current_timestamp():
    return datetime.now().strftime("%H:%M:%S")

async def main_async():
    async with websockets.serve(websocket_handler, "localhost", 6789):
        print("[WEBSOCKET] Server started on ws://localhost:6789")
        await asyncio.Future()  # Run forever

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def start_client(username):
    global username_global, client_socket_global, message_queue, loop_global

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"[ERROR] Could not connect: {e}")
        return

    username_global = username
    client_socket_global = client

    login_message = build_message("system", username, "login_request", timestamp=current_timestamp())
    client.send(encrypt_message(login_message))
    print(f"[SYSTEM] Connected to {SERVER_IP}:{SERVER_PORT} as '{username}'")

    receive_thread = threading.Thread(target=receive_messages, args=(client, username), daemon=True)
    receive_thread.start()

    if not is_port_in_use(6789):
        loop_global = asyncio.new_event_loop()
        asyncio.set_event_loop(loop_global)
        message_queue = asyncio.Queue()

        try:
            loop_global.run_until_complete(main_async())
        except KeyboardInterrupt:
            print("\n[SYSTEM] Shutting down...")
        finally:
            client.close()
            print("[SYSTEM] Connection closed.")
    else:
        print("[SYSTEM] WebSocket server already running, connecting to existing server")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[SYSTEM] Shutting down...")
        finally:
            client.close()
            print("[SYSTEM] Connection closed.")
