import sys
import socket
import threading
import base64
import os
import datetime
import json
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

import customtkinter as ctk
from customtkinter import CTkFont

from shared.encrypt import encrypt_message, decrypt_message
from shared.common import build_message, parse_message
from shared.config import SERVER_IP, SERVER_PORT, BUFFER_SIZE

class ChatWindow:
    def __init__(self):
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")  # "dark" or "light"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Modern Chatroom")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure grid weights for responsive design
        self.root.grid_columnconfigure(0, weight=3)  # Chat area (bigger)
        self.root.grid_columnconfigure(1, weight=1)  # User list (smaller)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Initialize variables
        self.username = None
        self.client = None
        self.pending_download_path = None
        self.pending_preview_filename = None
        
        self.setup_ui()
        self.setup_connection()
        
        # Start receiving messages in background thread
        threading.Thread(target=self.receive_messages, daemon=True).start()

    def setup_ui(self):
        # Left panel - Chat area
        self.chat_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.chat_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_frame.grid_rowconfigure(1, weight=1)

        self.download_frame = ctk.CTkScrollableFrame(self.chat_frame, height=120, corner_radius=10)
        self.download_frame.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        # Chat title
        self.chat_title = ctk.CTkLabel(
            self.chat_frame, 
            text="💬 Chat Messages", 
            font=CTkFont(size=18, weight="bold")
        )
        self.chat_title.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Chat display area
        self.chat_display = ctk.CTkTextbox(
            self.chat_frame,
            wrap="word",
            font=CTkFont(size=12),
            corner_radius=8
        )
        self.chat_display.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Message input area frame
        self.input_frame = ctk.CTkFrame(self.chat_frame, corner_radius=8)
        self.input_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(1, weight=1)
        
        # Receiver input
        self.receiver_label = ctk.CTkLabel(self.input_frame, text="To:", font=CTkFont(size=12))
        self.receiver_label.grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")
        
        self.receiver_input = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Leave blank for public chat",
            font=CTkFont(size=12),
            height=35
        )
        self.receiver_input.grid(row=0, column=1, padx=(0, 15), pady=10, sticky="ew")
        
        # Message input
        self.message_label = ctk.CTkLabel(self.input_frame, text="Message:", font=CTkFont(size=12))
        self.message_label.grid(row=1, column=0, padx=(15, 5), pady=(0, 10), sticky="w")
        
        # Message input and buttons frame
        self.message_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.message_frame.grid(row=1, column=1, padx=(0, 15), pady=(0, 10), sticky="ew")
        self.message_frame.grid_columnconfigure(0, weight=1)
        
        self.input_box = ctk.CTkEntry(
            self.message_frame,
            placeholder_text="Type your message here...",
            font=CTkFont(size=12),
            height=35
        )
        self.input_box.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.input_box.bind("<Return>", lambda e: self.send_message())
        
        self.send_button = ctk.CTkButton(
            self.message_frame,
            text="Send",
            width=80,
            height=35,
            font=CTkFont(size=12, weight="bold"),
            command=self.send_message
        )
        self.send_button.grid(row=0, column=1, padx=(0, 10))
        
        self.send_file_button = ctk.CTkButton(
            self.message_frame,
            text="📎 File",
            width=80,
            height=35,
            font=CTkFont(size=12),
            command=self.send_file
        )
        self.send_file_button.grid(row=0, column=2)
        
        # Right panel - Active users
        self.users_frame = ctk.CTkFrame(self.root, corner_radius=10)
        self.users_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        self.users_frame.grid_columnconfigure(0, weight=1)
        self.users_frame.grid_rowconfigure(1, weight=1)
        
        # Users title
        self.users_title = ctk.CTkLabel(
            self.users_frame, 
            text="👥 Active Users", 
            font=CTkFont(size=16, weight="bold")
        )
        self.users_title.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Users list
        self.active_users_list = ctk.CTkTextbox(
            self.users_frame,
            font=CTkFont(size=11),
            corner_radius=8,
            width=200
        )
        self.active_users_list.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def setup_connection(self):
        # Create custom dialog for username input
        dialog = ctk.CTkInputDialog(
            text="Enter your username:",
            title="Login to Chatroom"
        )
        username = dialog.get_input()
        
        if not username:
            messagebox.showerror("Error", "No username provided.")
            sys.exit()

        self.username = username
        self.root.title(f"Modern Chatroom - {self.username}")
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((SERVER_IP, SERVER_PORT))
            login_msg = build_message("system", self.username, "login_request")
            self.client.send(encrypt_message(login_msg))
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))
            sys.exit()

        self.append_to_chat(f"🟢 Connected as {self.username}", "system")

    def append_to_chat(self, message, msg_type="normal"):
        """Append message to chat display with proper formatting and color coding"""
        self.chat_display.configure(state="normal")
        
        # Add timestamp and formatting based on message type
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Configure text tags for colors if not already done
        self.chat_display.tag_config("blue", foreground="#4A9EFF")  # Blue for public messages
        self.chat_display.tag_config("red", foreground="#FF4A4A")   # Red for private messages
        #self.chat_display.tag_config("green", foreground="#4AFF4A") # Green for system messages
        #self.chat_display.tag_config("orange", foreground="#FFA54A") # Orange for file messages
        #self.chat_display.tag_config("gray", foreground="#AAAAAA")  # Gray for normal messages
        
        if msg_type == "system":
            formatted_msg = f"[{timestamp}] {message}\n"
            self.chat_display.insert("end", formatted_msg, "green")
        elif msg_type == "private_sent":
            formatted_msg = f"[{timestamp}] 🔒 You → {message}\n"
            self.chat_display.insert("end", formatted_msg, "red")
        elif msg_type == "private_received":
            formatted_msg = f"[{timestamp}] 🔒 {message}\n"
            self.chat_display.insert("end", formatted_msg, "red")
        elif msg_type == "public":
            formatted_msg = f"[{timestamp}] {message}\n"
            self.chat_display.insert("end", formatted_msg, "blue")
        elif msg_type == "file":
            formatted_msg = f"[{timestamp}] 📎 {message}\n"
            self.chat_display.insert("end", formatted_msg, "orange")
        else:
            formatted_msg = f"{message}\n"
            self.chat_display.insert("end", formatted_msg, "gray")
        
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")
        self.chat_display.insert("end", "\n")
    
    def handle_file_message(self, msg):
        sender = msg["sender"]
        filename = msg["message"]
        file_id = msg["file_id"]
        timestamp = msg["timestamp"]
        receiver = msg.get("receiver", "")

        if receiver:
            file_info = f"{sender} sent a file to {receiver}: {filename}"
        else:
            file_info = f"{sender} sent a file: {filename}"

        self.append_to_chat(f"[{timestamp}] 📎 {file_info}", "file")

        # Place download button in the scrollable download frame
        file_widget = self.create_file_widget(sender, filename, file_id)
        file_widget.pack(fill="x", padx=5, pady=4)

    def send_message(self):
        text = self.input_box.get().strip()
        receiver = self.receiver_input.get().strip()
        if not text:
            return

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if receiver == "":
            msg = build_message("public", self.username, text, timestamp=timestamp)
        else:
            msg = build_message("private", self.username, text, receiver=receiver, timestamp=timestamp)
            self.append_to_chat(f"{receiver}: {text}", "private_sent")

        self.client.send(encrypt_message(msg))
        self.input_box.delete(0, "end")

    def send_file(self):
        filepath = filedialog.askopenfilename(
            title="Select File to Send",
            filetypes=[
                ("All Files", "*.*"),
                ("PDF Files", "*.pdf"),
                ("Image Files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("Document Files", "*.docx *.doc *.txt"),
                ("Text Files", "*.txt")
            ]
        )
        if not filepath:
            return

        # Check file size (100MB limit)
        file_size = os.path.getsize(filepath)
        if file_size > 100 * 1024 * 1024:  # 100MB in bytes
            messagebox.showerror("File Too Large", "File size must be less than 100MB")
            return

        try:
            # Read file in binary mode
            with open(filepath, "rb") as f:
                file_data = f.read()

            # Encode to base64
            encoded = base64.b64encode(file_data).decode("utf-8")
            filename = os.path.basename(filepath)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            self.append_to_chat(f"Uploading {filename}... ({file_size} bytes)", "system")

            # Step 1: Send actual file data to server (upload step)
            upload_msg = {
                "type": "file_upload",
                "sender": self.username,
                "timestamp": timestamp,
                "filename": filename,
                "file_data": encoded
            }
            
            # Send message in chunks to handle large files
            upload_data = encrypt_message(json.dumps(upload_msg))
            self.client.sendall(upload_data)

            # Step 2: Notify others with file metadata (broadcast step)
            file_id = f"{timestamp.replace(':', '-')}_{filename}"
            receiver = self.receiver_input.get().strip()

            metadata_msg = {
                "type": "file",
                "sender": self.username,
                "timestamp": timestamp,
                "message": filename,
                "file_id": file_id
            }
            if receiver:
                metadata_msg["receiver"] = receiver

            self.client.sendall(encrypt_message(json.dumps(metadata_msg)))

            # Display in UI
            self.append_to_chat(f"File sent: {filename}", "file")

        except Exception as e:
            messagebox.showerror("File Send Error", f"Error sending file: {str(e)}")
            print(f"[FILE SEND ERROR] {e}")

    def create_file_widget(self, sender, filename, file_id):
        """Create a file download widget to insert into the download area"""
        file_frame = ctk.CTkFrame(self.download_frame, corner_radius=8, height=40)
        file_frame.pack_propagate(False)

        file_label = ctk.CTkLabel(
            file_frame,
            text=f"{filename} from {sender}",
            font=CTkFont(size=11)
        )
        file_label.pack(side="left", padx=10)

        download_btn = ctk.CTkButton(
            file_frame,
            text="Download",
            width=80,
            height=30,
            font=CTkFont(size=10),
            command=lambda: self.download_file(filename, file_id)
        )
        download_btn.pack(side="right", padx=10)

        return file_frame

    
    def download_file(self, filename, file_id):
        """Download a file from the server"""
        save_path = filedialog.asksaveasfilename(
            title="Save File As",
            initialname=filename,
            filetypes=[("All Files", "*.*")]
        )
        if save_path:
            try:
                request_msg = {
                    "type": "file_download_request",
                    "sender": self.username,
                    "file_id": file_id,
                }
                self.client.send(encrypt_message(json.dumps(request_msg)))
                self.pending_download_path = save_path
                self.append_to_chat(f"Downloading {filename}...", "system")
            except Exception as e:
                messagebox.showerror("Download Error", str(e))

    def update_users_list(self, users):
        """Update the active users list"""
        self.active_users_list.configure(state="normal")
        self.active_users_list.delete("1.0", "end")
        
        for i, user in enumerate(users, 1):
            user = user.strip()
            if user == self.username:
                self.active_users_list.insert("end", f"{i}. {user} (You)\n")
            else:
                self.active_users_list.insert("end", f"{i}. {user}\n")
        
        self.active_users_list.configure(state="disabled")

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(BUFFER_SIZE)
                if not data:
                    break
                decrypted = decrypt_message(data)
                msg = parse_message(decrypted)

                msg_type = msg.get("type")
                sender = msg.get("sender")
                message = msg.get("message")
                timestamp = msg.get("timestamp")
                receiver = msg.get("receiver", "")

                if msg_type == "public":
                    self.append_to_chat(f"{sender}: {message}", "public")

                elif msg_type == "private":
                    if sender == self.username:
                        self.append_to_chat(f"{receiver}: {message}", "private_sent")
                    else:
                        self.append_to_chat(f"{sender}: {message}", "private_received")

                elif msg_type == "system":
                    if message.startswith("user_list:"):
                        users = message.split(":", 1)[1].split(",")
                        # Use after() to safely update GUI from thread
                        self.root.after(0, lambda u=users: self.update_users_list(u))
                    else:
                        self.root.after(0, lambda m=message: self.append_to_chat(m, "system"))

                elif msg_type == "file":
                    # Use after() to safely handle file message from thread
                    self.root.after(0, lambda m=msg: self.handle_file_message(m))

                elif msg_type == "file_download":
                    filename = msg.get("message")
                    file_data = msg.get("file_data")
                    
                    if hasattr(self, 'pending_download_path') and self.pending_download_path:
                        try:
                            with open(self.pending_download_path, "wb") as f:
                                f.write(base64.b64decode(file_data))
                            self.root.after(0, lambda: self.append_to_chat(f"Downloaded: {filename}", "system"))
                            self.pending_download_path = None
                        except Exception as e:
                            self.root.after(0, lambda: messagebox.showerror("Download Error", str(e)))

            except Exception as e:
                print(f"[RECEIVE ERROR] {e}")
                break

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ChatWindow()
    app.run()
