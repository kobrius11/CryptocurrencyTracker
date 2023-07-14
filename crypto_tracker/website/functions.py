

from crypto_tracker.local_settings import KEY_INSTANCE
from cryptography.fernet import Fernet


CRYPTOGRAPHIC_KEY = Fernet(KEY_INSTANCE)


def sort_time(list):
    return list[3]
