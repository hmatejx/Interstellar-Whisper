#!/usr/bin/python3

'''bob

Usage:
  bob.py -m MSG
  bob.py (-h | --help)
  bob.py --version

Options:
  -h --help     Show this screen.
  -m MSG        The message string.
'''
from docopt import docopt

# stellar-base
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.utils import StellarMnemonic
# Stellar Whisper
from whisperer import Whisperer


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


if __name__ == '__main__':

    # Get cmdline arguments
    arguments = docopt(__doc__, version = 'bob 0.1')
    msg = arguments.get('-m')

    # Send message
    W.Send(Alice, msg.encode())
