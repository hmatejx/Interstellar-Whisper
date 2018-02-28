# stellar-base
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.builder import Builder
from stellar_base.utils import StellarMnemonic
# nacl
from nacl.public import Box
# misc
import base64
# utilities
from utils import *

DEBUG = False

# Create Alice's keypair
sm = StellarMnemonic("english")
m = "adjust razor stage use dish call door diary casino digital trend angle"
kp = Keypair.deterministic(m, lang = 'english')

# check that we have the right account for bob
Alice = "GCU2RRJHYBEIP6R6SJHLTCC32FVFGATYMTYB3ZBKT3OMPZLCTVSS7ZDH"
seed = kp.seed().decode()
assert Alice == kp.address().decode()

# Bob's address is GD2TA2JCQTM6ILRQB2JL3GIZSUKHVU5MDJSHRLM7VMNORLT6SZB72TIY
Bob = "GD2TA2JCQTM6ILRQB2JL3GIZSUKHVU5MDJSHRLM7VMNORLT6SZB72TIY"

# For NaCl we need to convert the Ed25519 keypair to Curve25519 keypair
skalice, pkalice = CurveKeyPair(kp)
pkbob = CurvePublicKey(Keypair.from_address(Bob))

# Alice creates a second box with her private key to decrypt the message
alice_box = Box(skalice, pkbob)

if DEBUG:
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃ Shared key information                 ┃")
    print("┗━BEGIN━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print("{}".format(base64.b16encode(alice_box.shared_key()).decode()))
    print("━━END━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

# check recent payments
address = Address(Alice)
res =(address.transactions(limit = 100))

# extract the message (assume last two transactions)
part1 = part2 = None
for record in res['_embedded']['records']:
    if record['memo_type'] == 'hash':
        part1 = part2
        part2 = record['memo']

# decode
part1 = base64.b64decode(part1)
part2 = base64.b64decode(part2)

if DEBUG:
    print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃ Encrypted payload                      ┃")
    print("┗━BEGIN━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
    print(base64.b16encode(part1).decode())
    print(base64.b16encode(part2).decode())
    print("━━END━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

encrypted = part1 + part2.rstrip(b'\0')

# Decrypt our message, an exception will be raised if the encryption was
#   tampered with or there was otherwise an error.
plaintext = alice_box.decrypt(encrypted)


print("┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
print("┃ Message from Bob!                      ┃")
print("┗━BEGIN━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")
print(plaintext.decode())
print("━━END━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
