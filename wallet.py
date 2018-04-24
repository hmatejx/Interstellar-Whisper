#import bcrypt
#from Crypto.Cipher import AES


def LoadWallet(name, passphrase):
    seed = open(name).readline()
    return seed


def SaveWallet(name, passphrase, seed):
    return None