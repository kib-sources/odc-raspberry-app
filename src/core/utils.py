import time
import uuid


def is_hex(string_to_check: str, hex_string_length: int) -> bool:
    if len(string_to_check) != hex_string_length:
        return False
    try:
        int(string_to_check, 16)
    except:
        return False
    return True


def current_epoch_time():
    return int(time.time())


def verify_time_is_near_current(t, epsilon):
    diff = current_epoch_time() - t
    return 0 <= diff <= epsilon


def gen_uuid() -> str:
    return str(uuid.uuid4())
