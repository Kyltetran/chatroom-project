import socket
import sys
import threading
from datetime import datetime
from client import gui
from shared.encrypt import encrypt_message, decrypt_message
from shared.common import build_message, parse_message
from shared.config import SERVER_IP, SERVER_PORT, BUFFER_SIZE
import base64
import os
import json

EMOJI_MAP = {
    ":smile:": "😄",
    ":heart:": "❤️",
    ":laugh:": "😂",
    ":sad:": "😢",
    ":thumbsup:": "👍",
    ":fire:": "🔥",
}

def apply_emoji(text):
    for code, emoji in EMOJI_MAP.items():
        text = text.replace(code, emoji)
    return text

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
            raw_message = msg.get("message", "")
            message = apply_emoji(raw_message)
            receiver = msg.get("receiver", None)
            timestamp = msg.get("timestamp", "")

            if msg_type == "system":
                if message.startswith("user_list:"):
                    users = message.split(":", 1)[1].split(",")
                    print(f"[USERS] Active users: {', '.join(users)}")
                else:
                    print(f"[SYSTEM] {message}")
                    
            elif msg_type == "public":
                print(f"(Global) {timestamp} {sender} > {message}")
                
            elif msg_type == "private":
                if sender == username:
                    print(f"(Private to {receiver}) {timestamp}: {message}")
                else:
                    print(f"(Private) {sender} {timestamp}: {message}")

            elif msg_type == "file_notify":
                # GUI will use this to create the message with a button
                filename = msg["filename"]
                sender = msg["sender"]
                receiver = msg.get("receiver", "")
                file_id = msg["file_id"]
                timestamp = msg["timestamp"]

                gui.display_file_message(sender, filename, file_id, timestamp, receiver)

            elif msg_type == "file_chunk":
                file_id = msg["file_id"]
                chunk_data = base64.b64decode(msg["chunk_data"])
                chunk_index = msg["chunk_index"]
                filename = msg["filename"]

                # Accumulate file chunks in memory or write to disk incrementally (to be handled in gui.py or helper)
                gui.receive_file_chunk(file_id, filename, chunk_index, chunk_data)

            elif msg_type == "file_download_complete":
                file_id = msg["file_id"]
                filename = msg["filename"]
                gui.complete_file_download(file_id, filename)

        except Exception as e:
            print(f"[RECEIVE ERROR] {e}")
            break

def current_timestamp():
    return datetime.now().strftime("%H:%M:%S")

def send_file(sock, filepath, receiver, username):
    if not os.path.exists(filepath):
        print("[ERROR] File not found.")
        return

    try:
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        timestamp = current_timestamp()
        file_id = f"{timestamp.replace(':', '-')}_{filename}"

        # Step 1: Notify server with metadata
        metadata_msg = {
            "type": "file_metadata",
            "sender": username,
            "timestamp": timestamp,
            "filename": filename,
            "file_id": file_id,
            "receiver": receiver or ""
        }
        sock.sendall(encrypt_message(json.dumps(metadata_msg)))

        # Step 2: Send file in chunks
        with open(filepath, "rb") as f:
            chunk_index = 0
            while True:
                chunk = f.read(4096)
                if not chunk:
                    break
                chunk_msg = {
                    "type": "file_chunk",
                    "sender": username,
                    "timestamp": timestamp,
                    "filename": filename,
                    "file_id": file_id,
                    "chunk_index": chunk_index,
                    "chunk_data": base64.b64encode(chunk).decode("utf-8"),
                }
                sock.sendall(encrypt_message(json.dumps(chunk_msg)))
                chunk_index += 1

        # Step 3: Notify upload is complete
        done_msg = {
            "type": "file_upload_done",
            "sender": username,
            "timestamp": timestamp,
            "filename": filename,
            "file_id": file_id
        }
        sock.sendall(encrypt_message(json.dumps(done_msg)))

    except Exception as e:
        print(f"[ERROR] File upload failed: {e}")

def request_file_download(sock, file_id, username):
    try:
        request_msg = {
            "type": "file_download_request",
            "sender": username,
            "file_id": file_id,
        }
        sock.send(encrypt_message(json.dumps(request_msg)))
    except Exception as e:
        print(f"[ERROR] Download request failed: {e}")

def main():
    username = input("Enter your username: ").strip()
    if not username:
        print("[ERROR] Username cannot be empty.")
        return

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"[ERROR] Could not connect: {e}")
        return

    # Send login request
    login_message = build_message("system", username, "login_request", timestamp=current_timestamp())
    client.send(encrypt_message(login_message))
    print(f"[SYSTEM] Connected to {SERVER_IP}:{SERVER_PORT} as '{username}'")

    # Start receiver thread
    threading.Thread(target=receive_messages, args=(client, username), daemon=True).start()

    while True:
        try:
            text = input().strip()
            if not text:
                continue

            timestamp = current_timestamp()
            text_with_emoji = apply_emoji(text)

            if text.startswith("/w "):
                parts = text.split(" ", 2)
                if len(parts) < 3:
                    print("[ERROR] Invalid private message format. Use /w username message")
                    continue
                receiver, msg_content = parts[1], parts[2]
                msg_content_with_emoji = apply_emoji(msg_content)
                msg = build_message("private", username, msg_content_with_emoji, receiver=receiver, timestamp=timestamp)
                print(f"(Private to {receiver}) {timestamp}: {msg_content_with_emoji}")
            else:
                msg = build_message("public", username, text_with_emoji, timestamp=timestamp)

            client.send(encrypt_message(msg))

        except KeyboardInterrupt:
            print("\n[SYSTEM] Exiting chat...")
            break
        except Exception as e:
            print(f"[SEND ERROR] {e}")
            break

    # Send disconnect message
    try:
        disconnect_msg = build_message("system", username, "disconnect", timestamp=current_timestamp())
        client.send(encrypt_message(disconnect_msg))
    except:
        pass

    client.close()
    print("[SYSTEM] Connection closed.")

if __name__ == "__main__":
    main()