import json
import threading
import socket
import base64
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.config import SERVER_IP, SERVER_PORT, BUFFER_SIZE
from shared.common import parse_message, build_message, current_timestamp
from shared.encrypt import encrypt_message, decrypt_message

clients = {}  # username → client socket
lock = threading.Lock()

FILE_STORAGE_DIR = "server_storage"
os.makedirs(FILE_STORAGE_DIR, exist_ok=True)

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

def broadcast_user_list():
    user_list = ",".join(clients.keys())
    message = build_message("system", "server", f"user_list:{user_list}")
    for conn in clients.values():
        try:
            conn.send(encrypt_message(message))
        except:
            pass

def recv_full_message(conn):
    """Receive a complete message from the client"""
    try:
        # First, try to receive data
        data = conn.recv(BUFFER_SIZE)
        if not data:
            return None
            
        # Try to decrypt and parse
        decrypted = decrypt_message(data)
        msg = parse_message(decrypted)
        return msg
    except Exception as e:
        print(f"[RECV ERROR] {e}")
        return None

def handle_client(conn, addr):
    username = None
    try:
        # Step 1: Receive initial username
        msg = recv_full_message(conn)
        if not msg:
            conn.close()
            return
            
        temp_name = msg.get("sender")

        with lock:
            if temp_name in clients:
                rejection = build_message("system", "server", "username_rejected")
                conn.send(encrypt_message(rejection))
                print(f"[REJECTED] {temp_name} already exists. Closing connection.")
                conn.close()
                return
            else:
                clients[temp_name] = conn
                username = temp_name
                broadcast_user_list()
                print(f"[CLIENTS] Now connected: {list(clients.keys())}")

        print(f"[CONNECTED] {username} from {addr}")

        # Step 2: Notify others
        join_msg = build_message("system", "server", f"{username} has joined the chat.")
        broadcast(join_msg, exclude=username)

        # Step 3: Main receive loop
        while True:
            msg = recv_full_message(conn)
            if not msg:
                break

            msg_type = msg.get("type")
            sender = msg.get("sender")
            timestamp = msg.get("timestamp", current_timestamp())
            text = msg.get("message", "")

            print(f"[DEBUG] Received message type: {msg_type} from {sender}")

            if msg_type == "public":
                print(f"[PUBLIC] {sender}: {text}")
                broadcast(json.dumps(msg))

            elif msg_type == "private":
                receiver = msg.get("receiver")
                if receiver in clients:
                    print(f"[PRIVATE] {sender} → {receiver}: {text}")
                    clients[receiver].send(encrypt_message(json.dumps(msg)))
                else:
                    error = build_message("system", "server", f"User '{receiver}' not found.")
                    conn.send(encrypt_message(error))

            elif msg_type == "file_upload":
                # Handle file upload
                filename = msg.get("filename")
                file_data_b64 = msg.get("file_data")
                timestamp = msg.get("timestamp")
                
                if not file_data_b64:
                    print(f"[ERROR] No file data received for {filename}")
                    continue
                
                try:
                    # Decode the base64 file data
                    file_data = base64.b64decode(file_data_b64)
                    file_id = f"{timestamp.replace(':', '-')}_{filename}"
                    filepath = os.path.join(FILE_STORAGE_DIR, file_id)
                    
                    # Save file to disk
                    with open(filepath, "wb") as f:
                        f.write(file_data)
                    
                    print(f"[UPLOAD] Saved file '{filename}' as '{file_id}' ({len(file_data)} bytes)")
                    
                    # Send confirmation back to sender
                    confirm_msg = build_message("system", "server", f"File '{filename}' uploaded successfully")
                    conn.send(encrypt_message(confirm_msg))
                    
                except Exception as e:
                    print(f"[ERROR] Failed to save uploaded file '{filename}': {e}")
                    error_msg = build_message("system", "server", f"Failed to upload file: {e}")
                    conn.send(encrypt_message(error_msg))

            elif msg_type == "file":
                # Handle file sharing notification
                receiver = msg.get("receiver")
                filename = msg.get("message")
                file_id = msg.get("file_id")
                
                print(f"[FILE] {sender} sharing file '{filename}' (ID: {file_id})")

                if receiver:
                    # Private file share
                    if receiver in clients:
                        print(f"[FILE] {sender} → {receiver}: {filename}")
                        clients[receiver].send(encrypt_message(json.dumps(msg)))
                    else:
                        error = build_message("system", "server", f"User '{receiver}' not found.")
                        conn.send(encrypt_message(error))
                else:
                    # Public file share
                    print(f"[FILE] {sender} shared file publicly: {filename}")
                    broadcast(json.dumps(msg), exclude=sender)

            elif msg_type == "file_download_request":
                # Handle file download request
                file_id = msg.get("file_id")
                requester = msg.get("sender")
                filepath = os.path.join(FILE_STORAGE_DIR, file_id)

                print(f"[DOWNLOAD] {requester} requesting file '{file_id}'")

                if not os.path.exists(filepath):
                    print(f"[ERROR] File '{file_id}' not found")
                    error_msg = build_message("system", "server", f"File '{file_id}' not found")
                    conn.send(encrypt_message(error_msg))
                    continue

                try:
                    with open(filepath, "rb") as f:
                        file_data = f.read()
                    
                    # Encode to base64
                    file_data_b64 = base64.b64encode(file_data).decode("utf-8")
                    
                    # Extract original filename (remove timestamp prefix)
                    original_filename = "_".join(file_id.split("_")[1:])

                    download_msg = {
                        "type": "file_download",
                        "sender": "server",
                        "timestamp": current_timestamp(),
                        "message": original_filename,
                        "file_data": file_data_b64
                    }
                    
                    clients[requester].send(encrypt_message(json.dumps(download_msg)))
                    print(f"[DOWNLOAD] Sent file '{file_id}' to {requester} ({len(file_data)} bytes)")

                except Exception as e:
                    print(f"[ERROR] Could not send file '{file_id}': {e}")
                    error_msg = build_message("system", "server", f"Error downloading file: {e}")
                    conn.send(encrypt_message(error_msg))

    except Exception as e:
        print(f"[EXCEPTION] {username}: {e}")

    finally:
        # Step 4: Clean up on disconnect
        if username:
            with lock:
                clients.pop(username, None)
                broadcast_user_list()
                print(f"[CLIENTS] Now connected: {list(clients.keys())}")
            leave_msg = build_message("system", "server", f"{username} has left the chat.")
            broadcast(leave_msg)
            print(f"[DISCONNECTED] {username} from {addr}")
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)
    print(f"[STARTED] Chat server on {SERVER_IP}:{SERVER_PORT}")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Server shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()