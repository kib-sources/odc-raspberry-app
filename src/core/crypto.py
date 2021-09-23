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


def hash_(*values):
    salt = 'eRgjPi235ps1'
    v = salt
    for value in values:
        value = str(value)
        v += '|' + value

    hex_hash = sha256(v.encode('utf-8')).hexdigest()
    return hex_hash


def signature(hex_hash: str, privkey: str) -> str:
    # rsa.PublicKey.load_pkcs1(pubkey)
    assert len(hex_hash) == 64

    _privkey = rsa.PrivateKey.load_pkcs1(privkey.encode())

    _hash = bytes(bytearray.fromhex(hex_hash))

    hex_signature = rsa.sign(_hash, _privkey, 'SHA-256').hex()

    return hex_signature


def verify_signature(hex_hash: str, hex_signature: str, publickey: str) -> bool:
    assert len(hex_hash) == 64
    _publickey = rsa.PublicKey.load_pkcs1(publickey.encode())

    _hash = bytes(bytearray.fromhex(hex_hash))
    _signature = bytes(bytearray.fromhex(hex_signature))

    # _check_hex_hash = rsa.decrypt(_signature, _publickey).hex()

    try:
        a = rsa.find_signature_hash(_signature, _publickey)
        rsa.verify(_hash, _signature, _publickey)
    except rsa.VerificationError:
        return False
    else:
        return True
