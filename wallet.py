import privy
import os.path
import os


def LoadWallet(name, passphrase):
    '''
    Retrieve the Stellar account secret key from the provided
    wallet file using the provided passphrase.

    Args:
        name: The name of the wallet file.
        passphrase: The passphrase used to encrypt the secret key.

    Returns:
        The secret key of the Stellar account as byte array.
    '''
    if not os.path.isfile(name) and os.access(name, os.R_OK):
        print("\nError: cannot open file {}!".format(name))
        return None

    seed = None
    try:
        encrypted = open(name).readline()
        seed = privy.peek(encrypted, passphrase)
    except (ValueError):
        print('\nError: Unable to decrypt the seed using the provided password!')

    return seed


def SaveWallet(name, passphrase, seed):
    '''
    Save the Stellar account secret key to the provided
    wallet file and encrypt using the provided passphrase.

    Args:
        name: The name of the wallet file.
        passphrase: The passphrase used to encrypt the secret key.
        seed: The Stellar secret key.

    Returns:
        True if save successful, False otherwise.
    '''
    if os.path.isfile(name):
        print("Error: file {} already exists!".format(name))
        return False

    encrypted = privy.hide(seed, passphrase, security = 2, server = False)

    file = open(name, mode = 'w')
    file.write(encrypted)
    file.close()

    return True
