import nacl.utils
from nacl.encoding import HexEncoder
from nacl.public import PrivateKey, SealedBox
import base64

# Generate Bob's private key, as we've done in the Box example
skbob = PrivateKey.generate()
pkbob = skbob.public_key

# Alice wishes to send a encrypted message to Bob,
# but prefers the message to be untraceable
sealed_box = SealedBox(pkbob)

# This is Alice's message
message = b"Kill all the kittens"

# Encrypt the message, it will carry the ephemeral key public part
# to let Bob decrypt it
encrypted = sealed_box.encrypt(message)

unseal_box = SealedBox(skbob)
# decrypt the received message
plaintext = unseal_box.decrypt(encrypted)

print("Message (%d):\n\t%s\n" % (len(message), message.decode()))
print("Encrypted (%d):\n\t%s\n" % (len(encrypted), base64.b16encode(encrypted).decode()))
print("Plaintext (%d):\n\t%s\n" % (len(plaintext), plaintext.decode()))
