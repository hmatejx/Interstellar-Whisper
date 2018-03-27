#!/usr/bin/python3

# stellar-base
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.builder import Builder
from stellar_base.utils import StellarMnemonic
# Stellar Whisper
from whisper import Whisperer

# Create Bob's keypair
sm = StellarMnemonic("english")
m = "sure hour arena purpose stairs shrug proud biology tobacco ahead shy stereo"
kp = Keypair.deterministic(m, lang = 'english')

# check that we have the right account for bob
MyAddress = "GD2TA2JCQTM6ILRQB2JL3GIZSUKHVU5MDJSHRLM7VMNORLT6SZB72TIY"
assert MyAddress == kp.address().decode()

# Alice's address
Alice = "GCU2RRJHYBEIP6R6SJHLTCC32FVFGATYMTYB3ZBKT3OMPZLCTVSS7ZDH"

W = Whisperer(kp)
W.Send(Alice, "Hi Alice!")
