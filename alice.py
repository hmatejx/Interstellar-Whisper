#!/usr/bin/python3

'''alice

Usage:
  alice.py [-n N]
  alice.py (-h | --help)
  alice.py --version

Options:
  -h --help     Show this screen.
  -n N          Read N last messages [default: 1].
'''
from docopt import docopt
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


if __name__ == '__main__':

    # Get cmdline arguments
    arguments = docopt(__doc__, version = 'alice 0.1')
    n = int(arguments.get('-n'))

    # Read n last messages
    msg = W.Read(address = Bob, tail = n)

    # Display messages
    print('Last {} messages...'.format(n))
    for i in range(0, len(msg)):
        print('{:>3}) '.format(i + 1), end='')
        print(''.join([s if ord(s) < 127 and ord(s) > 31 else ' ' for s in msg[i].decode('utf-8', errors='ignore')]))
