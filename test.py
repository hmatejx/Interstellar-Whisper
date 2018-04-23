from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
backend = default_backend()

key = b'\x00' * 32
print(base64.b16encode(key).decode())
iv = b'\x00' * 16

cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
encryptor = cipher.encryptor()
ct = encryptor.update(b"a secret message") + encryptor.finalize()
print(base64.b16encode(ct).decode())

decryptor = cipher.decryptor()
decryptor.update(ct) + decryptor.finalize()