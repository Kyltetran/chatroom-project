import json
import threading
import socket
from shared.config import SERVER_IP, SERVER_PORT, BUFFER_SIZE
from shared.common import parse_message, build_message, current_timestamp
from shared.encrypt import encrypt_message, decrypt_message
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

clients = {}  # username → client socket
lock = threading.Lock()


def broadcast(json_data, exclude=None):
    """
    Send a JSON-formatted message to all connected users except 'exclude'.
    """
    for user, conn in clients.items():
        if user != exclude:
            try:
                conn.send(encrypt_message(json_data))
            except:
                print(f"[ERROR] Failed to send to {user}")


def handle_client(conn, addr):
    username = None
    try:
        # Step 1: Receive initial username
        encrypted = conn.recv(BUFFER_SIZE)
        raw = decrypt_message(encrypted)
        msg = parse_message(raw)
        # username = msg.get("sender")
        temp_name = msg.get("sender")

        with lock:
            if temp_name in clients:
                rejection = build_message(
                    "system", "server", "username_rejected")
                conn.send(encrypt_message(rejection))
                print(
                    f"[REJECTED] {temp_name} already exists. Closing connection.")
                conn.close()
                return
            else:
                clients[temp_name] = conn
                username = temp_name
                print(f"[CLIENTS] Now connected: {list(clients.keys())}")

        print(f"[CONNECTED] {username} from {addr}")

        # Step 2: Notify others
        join_msg = build_message(
            "system", "server", f"{username} has joined the chat.")
        broadcast(join_msg, exclude=username)

        # Step 3: Main receive loop
        while True:
            encrypted = conn.recv(BUFFER_SIZE)
            if not encrypted:
                break

            raw = decrypt_message(encrypted)
            msg = parse_message(raw)

            msg_type = msg.get("type")
            sender = msg.get("sender")
            timestamp = msg.get("timestamp", current_timestamp())
            text = msg.get("message")

            if msg_type == "public":
                print(f"[PUBLIC] {sender}: {text}")
                broadcast(json.dumps(msg))

            elif msg_type == "private":
                receiver = msg.get("receiver")
                if receiver in clients:
                    print(f"[PRIVATE] {sender} → {receiver}: {text}")
                    clients[receiver].send(encrypt_message(json.dumps(msg)))
                else:
                    error = build_message(
                        "system", "server", f"User '{receiver}' not found.")
                    conn.send(encrypt_message(error))

            # More types (e.g., file) will be added in Phase 6

    except Exception as e:
        print(f"[EXCEPTION] {e}")

    finally:
        # Step 4: Clean up on disconnect
        if username:
            with lock:
                clients.pop(username, None)
                print(f"[CLIENTS] Now connected: {list(clients.keys())}")
            leave_msg = build_message(
                "system", "server", f"{username} has left the chat.")
            broadcast(leave_msg)
            print(f"[DISCONNECTED] {username} from {addr}")
            conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen()
    print(f"[STARTED] Chat server on {SERVER_IP}:{SERVER_PORT}")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(
            conn, addr), daemon=True).start()


if __name__ == "__main__":
    start_server()
