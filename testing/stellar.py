from stellar_base.keypair import Keypair
from stellar_base.utils import StellarMnemonic, encode_check, calculate_checksum
import nacl.utils
from nacl.public import PrivateKey, Box, PublicKey
from nacl.signing import SigningKey, VerifyKey
import base64
import ed25519


def Ed25519_to_Curve25519(kp):
    sk = PrivateKey(SigningKey(kp.raw_seed()).to_curve25519_private_key()._private_key)
    pk = PublicKey(VerifyKey(kp.raw_public_key()).to_curve25519_public_key()._public_key)

    return sk, pk


def info_kp(kp, name):
    print("\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃ Keypair information for {:14} ┃".format(name))
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    print("\nStellar format")
    print("────────────────────────────────────────────────────────────────────────────────────────")
    print("Secret key (SEED)     \t{}".format(encode_check('seed', kp.raw_seed()).decode()))
    print("Public key (ADDRESS)  \t{}".format(encode_check('account', kp.raw_public_key()).decode()))

    print("\n ⇨ Ed25519 keypair")
    print("────────────────────────────────────────────────────────────────────────────────────────")
    print("Secret key            \t{}".format(base64.b16encode(kp.raw_seed()).decode()))
    print("Public key            \t{}".format(base64.b16encode(kp.raw_public_key()).decode()))

    sk, pk = Ed25519_to_Curve25519(kp)
    print("\n ⇨ Curve25519 keypair")
    print("────────────────────────────────────────────────────────────────────────────────────────")
    print("Secret key            \t{}".format(base64.b16encode(sk._private_key).decode()))
    print("Public key            \t{}".format(base64.b16encode(pk._public_key).decode()))


sm = StellarMnemonic("english")
m_alice = "adjust razor stage use dish call door diary casino digital trend angle"
m_bob = "sure hour arena purpose stairs shrug proud biology tobacco ahead shy stereo"

# Now we use the mnemonic string m to generate the key pair:
kp_alice = Keypair.deterministic(m_alice, lang = 'english')
kp_bob = Keypair.deterministic(m_bob, lang = 'english')

# Display some handy info about the keypair
info_kp(kp_alice, "Alice")
info_kp(kp_bob, "Bob")

# For NaCl we need to convert the Ed25519 keypair to Curve25519 keypair
skbob, pkbob = Ed25519_to_Curve25519(kp_bob)
skalice, pkalice = Ed25519_to_Curve25519(kp_alice)

# Bob wishes to send Alice an encrypted message so Bob must make a Box with
#   his private key and Alice's public key
bob_box = Box(skbob, pkalice)

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

print("\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃ Shared key information                 ┃")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print("\nShared key according to Bob:   {}".format(base64.b16encode(bob_box.shared_key()).decode()))
print("Shared key according to Alice: {}".format(base64.b16encode(alice_box.shared_key()).decode()))

# Decrypt our message, an exception will be raised if the encryption was
#   tampered with or there was otherwise an error.
plaintext = alice_box.decrypt(encrypted)

def split2len(s, n):
    def _f(s, n):
        while s:
            yield s[:n]
            s = s[n:]
    return list(_f(s, n))

print("\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃ First transmission                     ┃")
print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print("\nMessage ({})".format(len(message)))
print("────────────────────────────────────────────────────────────────────────────────────────")
print("\t{}".format(message.decode()))
print("\nEncrypted ({})".format(len(encrypted)))
print("────────────────────────────────────────────────────────────────────────────────────────")
print("\t{}".format('\n\t'.join([base64.b16encode(l).decode() for l in split2len(encrypted, 32)])))
print("\nPlaintext ({})".format(len(plaintext)))
print("────────────────────────────────────────────────────────────────────────────────────────")
print("\t{}".format(plaintext.decode()))
