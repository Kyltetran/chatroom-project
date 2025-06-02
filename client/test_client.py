import socket
import json
from shared.encrypt import encrypt_message, decrypt_message
from shared.common import build_message, parse_message
from shared.config import SERVER_IP, SERVER_PORT, BUFFER_SIZE


def main():
    username = input("Enter your username: ")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    # Step 1: Send initial login
    login_msg = build_message("system", username, "login_request")
    client.send(encrypt_message(login_msg))

    # Step 2: Check server response
    data = client.recv(BUFFER_SIZE)
    response = parse_message(decrypt_message(data))
    if "rejected" in response["message"]:
        print("[❌] Username rejected. Try a different one.")
        client.close()
        return

    print("[✅] Logged in successfully.")

    # Step 3: Loop to send public messages
    try:
        while True:
            text = input("> ")
            if text.lower() == "/exit":
                break
            msg = build_message("public", username, text)
            client.send(encrypt_message(msg))
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        print("[Disconnected]")


if __name__ == "__main__":
    main()
