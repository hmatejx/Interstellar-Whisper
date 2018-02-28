# stellar-base
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.builder import Builder
from stellar_base.utils import StellarMnemonic
# nacl
import nacl.utils
from nacl.public import Box
# misc
import base64
# utilities
from utils import *

DEBUG = False

# Create Bob's keypair
sm = StellarMnemonic("english")
m = "sure hour arena purpose stairs shrug proud biology tobacco ahead shy stereo"
kp = Keypair.deterministic(m, lang = 'english')

# check that we have the right account for bob
Bob = "GD2TA2JCQTM6ILRQB2JL3GIZSUKHVU5MDJSHRLM7VMNORLT6SZB72TIY"
seed = kp.seed().decode()
assert Bob == kp.address().decode()

# Alice's address is GCU2RRJHYBEIP6R6SJHLTCC32FVFGATYMTYB3ZBKT3OMPZLCTVSS7ZDH
Alice = "GCU2RRJHYBEIP6R6SJHLTCC32FVFGATYMTYB3ZBKT3OMPZLCTVSS7ZDH"

# For NaCl we need to convert the Ed25519 keypair to Curve25519 keypair
skbob, pkbob = CurveKeyPair(kp)
pkalice = CurvePublicKey(Keypair.from_address(Alice))

# Bob wishes to send Alice an encrypted message so Bob must make a Box with
#   his private key and Alice's public key
bob_box = Box(skbob, pkalice)

if DEBUG:
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃ Shared key information                 ┃")
    print("┗━BEGIN━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print("{}".format(base64.b16encode(bob_box.shared_key()).decode()))
    print("━━END━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

# This is our message to send, it must be a bytestring as Box will treat it
#   as just a binary blob of data.
message = b"Hello world!"

# Encrypt our message, it will be exactly 40 bytes longer than the
#   original message as it stores authentication information and the
#   nonce alongside it.
nonce = nacl.utils.random(Box.NONCE_SIZE)
encrypted = bob_box.encrypt(message, nonce)

# split into two parts
part1 = encrypted[0:32]
part2 = encrypted[32:].ljust(32, b'\0')

print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃ Message for Alice!                     ┃")
print("┗━BEGIN━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print(message.decode())
print("━━END━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

# show the two parts
if DEBUG:
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃ Encrypted payload                      ┃")
    print("┗━BEGIN━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print(base64.b16encode(part1).decode())
    print(base64.b16encode(part2).decode())
    print("━━END━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

quit()

# send the secret message to Alice
# part 1
builder = Builder(secret = seed)
builder.append_payment_op(Alice, '0.0000001', 'XLM')
builder.add_hash_memo(part1)
builder.sign()
builder.submit()
# part 2
builder = Builder(secret = seed)
builder.append_payment_op(Alice, '0.0000001', 'XLM')
builder.add_hash_memo(part2.ljust(32, b'\0'))
builder.sign()
builder.submit()
s