import json
from datetime import datetime


def current_timestamp():
    return datetime.now().strftime("%H:%M:%S")


def build_message(msg_type, sender, message, receiver=None, file_data=None, timestamp=None):
    if not timestamp:
        timestamp = current_timestamp()
    msg = {
        "type": msg_type,
        "sender": sender,
        "timestamp": timestamp,
        "message": message
    }
    if receiver:
        msg["receiver"] = receiver
    if file_data:
        msg["file_data"] = file_data
    return json.dumps(msg)


def parse_message(json_string):
    return json.loads(json_string)
