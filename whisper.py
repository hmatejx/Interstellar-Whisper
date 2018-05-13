#!/usr/bin/python3

'''Interstellar Whisper.

Usage:
  whisper.py (-r [-n N] | -s MSG -a ADDR) [-k FILE] [-e ENC]
  whisper.py -h | --help
  whisper.py -v | --version

Options:
  -r            Read messages.
  -s MSG        The message text to send.
  -a ADDR       The destination address (required for sending).
  -n N          Read last N messages (optional for reading) [default: 1].
  -k FILE       Path to the file containing the password-protected stellar
                seed for your account [default: ~/.stellar/wallet].
  -e ENC        Required encoding for the message text [default: 0].
                Valid options are:
                  0 = raw (no) encoding,
                  1 = GSM 03.38 encoding,
                  2 = Sixbit ASCII encoding,
                  3 = smaz compression.
  -v --version  Display version and exit.
  -h --help     Show this screen.
'''
from docopt import docopt
import wallet
from getpass import getpass

# stellar-base
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.utils import StellarMnemonic
# Stellar Whisper
from whisperer import Whisperer


def banner():
    banner = """\
    ____  .   __            .    __       ___         .
 . /  _/___  / /____ *__________/ /____  / / /___ ______ +  /\\
   / // __ \/ __/ _ \/ ___/ ___/ __/ _ \/ / / __ `/ ___/  .'  '.
 _/ // / / / /_/  __/ /  (__  ) /_/  __/ / / /_/ / /     /======\\
/___/_/ /_____/\___/_/  /____/\__/\___/_/_/\__,_/_/     ;:.  _   ;
| |   . / / /_  (_)________  ___  _____                 |:. (_)  |
| | /| / / __ \/ / ___/ __ \/ _ \/ ___/            +    ;:.      ;
| |/ |/ / / / / (__  ) /_/ /  __/ /                   .' \:.XLM / `.
|__/|__/_/ /_/_/____/ .___/\___/_/     .        .    / .-'':._.'`-. \\
                   /_/                               |/    /||\    \|\

"""
    print(banner)


if __name__ == '__main__':

    banner()

    # Get cmdline arguments
    arguments = docopt(__doc__, version = 'Interstellar Whisper 0.1')

    # Load seed and kreate keypair
    try:
        password = getpass('Enter password: ')
    except KeyboardInterrupt:
        print()
        exit(-1)
    seed = wallet.LoadWallet(arguments.get('-k'), password)
    if seed == None:
        exit(-1)

    # Create a Whisperer instance
    kp = Keypair.from_seed(seed)
    W = Whisperer(kp)

    # Parse arguments
    if arguments.get('-r'):

        # Read last n messages
        n = int(arguments.get('-n'))
        msg = W.Read(tail = n, printable = False)

        # Display messages
        print('\nLast {} message(s)...'.format(n))
        for i in range(0, len(msg)):
            print('{:>3}) '.format(i + 1), end = '')
            print(msg[i].decode('utf-8', errors = 'ignore'))

    elif arguments.get('-s') is not None:
        # Check if message is provided
        msg = arguments.get('-s')

        #Check if receiving address is provided
        address = arguments.get('-a')
        if not Whisperer.ValidateAddress(address):
            print("Error: No valid Stellar destination address provided!")
            exit(-1)

        print("Sending message to {}...".format(address))
        W.Send(address, msg.encode(), int(arguments.get('-e')))
        print("Done.")
