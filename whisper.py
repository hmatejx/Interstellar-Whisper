#!/usr/bin/python3

'''whisper.

Usage:
  whisper.py (-r [-n N] | -s MSG -a ADDR) [-k FILE]
  whisper.py -h | --help
  whisper.py -v | --version

Options:
  -r            Read messages.
  -s MSG        The message text to send.
  -a ADDR       The destination address (required for sending).
  -n N          Read last N messages (optional for reading) [default: 1].
  -k FILE       Path to the file containing the password-protected stellar
                seed for your account [default: ~/.stellar/wallet].
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


if __name__ == '__main__':

    # Get cmdline arguments
    arguments = docopt(__doc__, version = 'Interstellar Whisper 0.1')

    # Load seed and kreate keypair
    password = getpass('Enter password: ')
    seed = wallet.LoadWallet(arguments.get('-k'), password)
    kp = Keypair.from_seed(seed)

    # Create a Whisperer instance
    W = Whisperer(kp)

    if arguments.get('-r'):

      # Read last n messages
      n = int(arguments.get('-n'))
      msg = W.Read(tail = n)

      # Display messages
      print('Last {} message(s)...'.format(n))
      for i in range(0, len(msg)):
        print('{:>3}) '.format(i + 1), end = '')
        print(''.join([s if ord(s) < 127 and ord(s) > 31 else ' ' for s in msg[i].decode('utf-8', errors = 'ignore')]))

    elif arguments.get('-s') is not None:
      # check if message
      msg = arguments.get('-s')

      # Check if receiving address is provided
      address = arguments.get('-a')
      if not Whisperer.ValidateAddress(address):
        print("Error: No valid Stellar destination address provided!")
        exit(-1)

      print("Sending message to {}...".format(address))
      W.Send(address, msg.encode())
      print("Done.")
