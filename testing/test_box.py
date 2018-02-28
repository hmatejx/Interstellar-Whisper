import nacl.utils
from nacl.public import PrivateKey, Box
import base64

# Generate Bob's private key, which must be kept secret
skbob = PrivateKey.generate()

# Bob's public key can be given to anyone wishing to send
#   Bob an encrypted message
pkbob = skbob.public_key

# Alice does the same and then Alice and Bob exchange public keys
skalice = PrivateKey.generate()
pkalice = skalice.public_key

print("skbob: %s" % base64.b16encode(skbob._private_key).decode())
print("pkbob: %s" % base64.b16encode(pkbob._public_key).decode())
print("skalice: %s" % base64.b16encode(skalice._private_key).decode())
print("pkalice: %s" % base64.b16encode(pkalice._public_key).decode())

# Bob wishes to send Alice an encrypted message so Bob must make a Box with
#   his private key and Alice's public key
bob_box = Box(skbob, pkalice)
print("Shared key according to Bob:   {}".format(base64.b16encode(bob_box.shared_key()).decode()))

# This is our message to send, it must be a bytestring as Box will treat it
#   as just a binary blob of data.
message = b"Kill all the kittens"

# Encrypt our message, it will be exactly 40 bytes longer than the
#   original message as it stores authentication information and the
#   nonce alongside it.
nonce = nacl.utils.random(Box.NONCE_SIZE)
encrypted = bob_box.encrypt(message, nonce)

# Alice creates a second box with her private key to decrypt the message
alice_box = Box(skalice, pkbob)
print("Shared key according to Alice: {}".format(base64.b16encode(alice_box.shared_key()).decode()))

# Decrypt our message, an exception will be raised if the encryption was
#   tampered with or there was otherwise an error.
plaintext = alice_box.decrypt(encrypted)

print("\nFirst transmission")
print("-------------------")
print("Message (%d):\n\t%s\n" % (len(message), message))
print("Encrypted (%d):\n\t%s\n" % (len(encrypted), base64.b16encode(encrypted)))
print("Plaintext (%d):\n\t%s\n" % (len(plaintext), plaintext))
