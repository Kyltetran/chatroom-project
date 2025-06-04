import sys
import socket
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox, QInputDialog
)
from PyQt5.QtCore import pyqtSignal, QObject
from shared.encrypt import encrypt_message, decrypt_message
from shared.common import build_message, parse_message
from shared.config import SERVER_IP, SERVER_PORT, BUFFER_SIZE


class ChatWindow(QWidget):
    message_received = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chatroom (Dummy GUI)")
        self.layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.input_box = QLineEdit()
        self.send_button = QPushButton("Send")

        self.layout.addWidget(self.chat_display)
        self.layout.addWidget(self.input_box)
        self.layout.addWidget(self.send_button)
        self.setLayout(self.layout)

        self.send_button.clicked.connect(self.send_message)

        self.username = None
        self.client = None
        self.setup_connection()

        # if not self.setup_connection():
        #     sys.exit()

        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.message_received.connect(self.chat_display.append)

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

                if msg_type == "public":
                    # Display public message from others
                    display = f"{sender}: {message}"
                    # self.chat_display.append(display)
                    self.message_received.emit(display)

                elif msg_type == "system":
                    self.chat_display.append(f"[{message}]")

                elif msg_type == "private":
                    # Optional for later
                    display = f"(Private) {sender}: {message}"
                    # self.chat_display.append(display)
                    self.message_received.emit(display)

            except Exception as e:
                print(f"[RECEIVE ERROR] {e}")
                break

    def setup_connection(self):
        username, ok = QInputDialog.getText(
            self, "Login", "Enter your username:")
        if not ok or not username:
            QMessageBox.critical(self, "Error", "No username provided.")
            sys.exit()

        self.username = username
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((SERVER_IP, SERVER_PORT))
            login_msg = build_message("system", self.username, "login_request")
            self.client.send(encrypt_message(login_msg))
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))
            sys.exit()

        self.chat_display.append(f"[Connected as {self.username}]")

    def send_message(self):
        text = self.input_box.text()
        if not text:
            return
        msg = build_message("public", self.username, text)
        self.client.send(encrypt_message(msg))
        # self.chat_display.append(f"{self.username}: {text}")
        self.input_box.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
