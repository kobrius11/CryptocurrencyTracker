from cryptography.fernet import Fernet
GENERATED_KEY = Fernet.generate_key()
CRYPTOGRAPHIC_KEY = Fernet(GENERATED_KEY)