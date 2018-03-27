#!/usr/bin/python3

# stellar-base
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.builder import Builder
from stellar_base.utils import StellarMnemonic
# Stellar Whisper
from whisper import Whisperer

# Create Alice's keypair
sm = StellarMnemonic("english")
m = "adjust razor stage use dish call door diary casino digital trend angle"
kp = Keypair.deterministic(m, lang = 'english')

# check that we have the right account for bob
MyAddress = "GCU2RRJHYBEIP6R6SJHLTCC32FVFGATYMTYB3ZBKT3OMPZLCTVSS7ZDH"
assert MyAddress == kp.address().decode()

# Bob's address is GD2TA2JCQTM6ILRQB2JL3GIZSUKHVU5MDJSHRLM7VMNORLT6SZB72TIY
Bob = "GD2TA2JCQTM6ILRQB2JL3GIZSUKHVU5MDJSHRLM7VMNORLT6SZB72TIY"

W = Whisperer(kp)
W.Send(Bob, "Hi Alice!")
