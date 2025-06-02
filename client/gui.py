import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton


class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chatroom")
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

    def send_message(self):
        text = self.input_box.text()
        self.chat_display.append(f"You: {text}")
        self.input_box.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())
