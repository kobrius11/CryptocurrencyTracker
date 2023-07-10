from cryptography.fernet import Fernet


KEY_INSTANCE = Fernet.generate_key()
print(KEY_INSTANCE)
