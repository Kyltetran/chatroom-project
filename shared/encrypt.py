from cryptography.fernet import Fernet

FERNET_KEY = b'BAim6q38GF8ecFfoPYT23o8e6QQ003MZifgpn8uLFWY='  # Replace with a real one
cipher = Fernet(FERNET_KEY)


def encrypt_message(message: str) -> bytes:
    return cipher.encrypt(message.encode())


def decrypt_message(encrypted: bytes) -> str:
    return cipher.decrypt(encrypted).decode()


# Comment the above code and use this to generate a new key:
# from cryptography.fernet import Fernet
# print(Fernet.generate_key())
