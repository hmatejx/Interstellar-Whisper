import privy
import os.path
import os


def LoadWallet(name, passphrase):
    '''
    '''
    if not os.path.isfile(name) and os.access(name, os.R_OK):
        print("Error: cannot open file {}!".format(name))
        return None

    encrypted = open(name).readline()
    seed = privy.peek(encrypted, passphrase)
    
    return seed


def SaveWallet(name, passphrase, seed):
    '''
    '''  
    if os.path.isfile(name):
        print("Error: file {} already exists!".format(name))
        return False
 
    encrypted = privy.hide(seed, passphrase, security = 2, server = False)
 
    file = open(name, mode = 'w')
    file.write(encrypted)
    file.close()
    
    return True