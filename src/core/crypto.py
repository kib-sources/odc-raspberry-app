from hashlib import sha256

import rsa


def hash_items(items):
    joined = " ".join([str(i) for i in items])
    joined += "]!L3bP9a@GM6U*LL"
    hex_hash = sha256(joined.encode()).hexdigest()
    return hex_hash


def sign_with_private_key(item, key):
    private_key = rsa.PrivateKey.load_pkcs1(key.encode())
    data = bytes(bytearray.fromhex(item))
    signed_data = rsa.sign(data, private_key, "SHA-256").hex()
    return signed_data


def verify_with_public_key(origin, signature, key):
    origin_bytes = bytes(bytearray.fromhex(origin))
    signature_bytes = bytes(bytearray.fromhex(signature))
    public_key = rsa.PublicKey.load_pkcs1(key.encode())

    try:
        rsa.verify(origin_bytes, signature_bytes, public_key)
    except rsa.VerificationError:
        return False
    return True


def init_pair():
    """
    Инициализирует пары ключей:
    * закрытый ключ шифрования
    * открытый ключ расшифрования
    :return:
    """

    pubkey, privkey = rsa.newkeys(512)

    pubkey = pubkey._save_pkcs1_pem().decode()
    privkey = privkey._save_pkcs1_pem().decode()

    return pubkey, privkey
