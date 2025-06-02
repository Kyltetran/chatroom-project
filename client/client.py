import socket
from shared.encrypt import encrypt_message, decrypt_message
from shared.common import build_message, parse_message
from shared.config import SERVER_IP, SERVER_PORT, BUFFER_SIZE


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    username = input("Username: ").strip()
    login_msg = build_message("system", username, "login_request")
    client.send(encrypt_message(login_msg))

    response = client.recv(BUFFER_SIZE)
    resp_obj = parse_message(decrypt_message(response))
    if "rejected" in resp_obj["message"]:
        print("[❌] Username rejected.")
        return
    print("[✅] Logged in as", username)

    # Main loop
    try:
        while True:
            msg_text = input("> ").strip()
            if msg_text.lower() == "/exit":
                break
            msg = build_message("public", username, msg_text)
            client.send(encrypt_message(msg))
    except KeyboardInterrupt:
        pass
    finally:
        client.close()
        print("[Disconnected]")


if __name__ == "__main__":
    main()
