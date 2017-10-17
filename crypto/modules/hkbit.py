from os import urandom

def crypt(data: bytes, key: bytes = None):
    output = []
    if not key:
        key = urandom(len(data))
    while len(key) < len(data):
        key += key
    key = key[:len(data)]
    for byte in data:
        binary = [(byte >> bit) & 1 for bit in range(7, -1, -1)]
        for k in f"{key[len(output)]:02x}":
            binary[int(k, 16) - (8 if k.isalpha() or int(k) >= 8 else 0)] ^= 1
        output.append(int("".join(map(str, binary)), 2))
    return bytes(output), key
