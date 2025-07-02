import socket
import sys
import threading
from datetime import datetime
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
            message = apply_emoji(msg.get("message"))
            receiver = msg.get("receiver", None)
            timestamp = msg.get("timestamp", "")

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

            text = apply_emoji(text)
            timestamp = current_timestamp()

            if text.startswith("/w "):
                parts = text.split(" ", 2)
                if len(parts) < 3:
                    print("[ERROR] Invalid private message format. Use /w username message")
                    continue
                receiver, msg_content = parts[1], parts[2]
                msg = build_message("private", username, msg_content, receiver=receiver, timestamp=timestamp)
                print(f"(Private to {receiver}) {timestamp}: {msg_content}")
            else:
                msg = build_message("public", username, text, timestamp=timestamp)

            client.send(encrypt_message(msg))

        except KeyboardInterrupt:
            print("\n[SYSTEM] Exiting chat...")
            try:
                disconnect_msg = build_message("system", username, "disconnect", timestamp=current_timestamp())
                client.send(encrypt_message(disconnect_msg))
            except:
                pass
            break
        except Exception as e:
            print(f"[SEND ERROR] {e}")
            break

    client.close()
    print("[SYSTEM] Connection closed.")


if __name__ == "__main__":
    main()
