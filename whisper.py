from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.utils import encode_check, decode_check
from stellar_base.horizon import horizon_testnet
from stellar_base.builder import Builder
from nacl.signing import SigningKey, VerifyKey
from nacl.bindings import crypto_box_beforenm
from Crypto.Cipher import AES
import base64
#import json
#import requests


__all__ = ['Whisperer']


# This creates a new Horizon Livenet instance
horizon = horizon_testnet()


def DumpBlocks(blocks):
    '''
    '''
    print('\nMessage blocks')
    print('────────────────────────────────────────────────────────────────────────────────────────')
    for i in range(0, len(blocks)):
        h = bin(blocks[i][0])[2:]
        h = '0' * (8 - len(h)) + h
        f = blocks[i][1:]
        print("{0}|{1}|{2}".format(h[0:5], h[5:8], f.decode()))
    print('────────────────────────────────────────────────────────────────────────────────────────')


def DumpEncrypted(encrypted):
    '''
    '''
    print('\nEncrypted blocks')
    print('────────────────────────────────────────────────────────────────────────────────────────')
    for i in range(0, len(encrypted)):
       print("{}".format(base64.b16encode(encrypted[i]).decode()))
    print('────────────────────────────────────────────────────────────────────────────────────────')


def ed25519_pk_to_curve25519_pk(pk):
    '''
    '''
    return VerifyKey(pk).to_curve25519_public_key()._public_key


def ed25519_sk_to_curve25519_pk(sk):
    '''
    '''
    return SigningKey(sk).to_curve25519_private_key()._private_key


class Whisperer:
    def __init__(self, kp):
        '''
        Initialize the Whisper class using your Stellar.

        Args:
            kp: This is your Stellar keypair, as encoded by the
                stellar_base.keypair class.

        Returns:
            Instance of the object.
        '''
        self.__kp = kp
        self.__sk = ed25519_sk_to_curve25519_pk(kp.raw_seed())
        self.__pk = ed25519_pk_to_curve25519_pk(kp.raw_public_key())


    @classmethod
    def __encode(cls, msg, enc):
        '''
        Encode the message using the required encoding,
        potentially save some preicous space.

        Args:
            mgs: The message to be encoded.
            enc: The desired encoding.

        Returns:
            The encoded message (TODO: currently just returns).
        '''
        return msg


    @classmethod
    def __encapsulate(cls, msg, encoding = 0):
        '''
        Encapsulate the message using the required encoding,
        split into fragments, add headers, and return the blocks.

        Args:
            mgs: The message to be encoded.
            enc: The desired encoding.

        Returns:
            The encoded message (TODO: currently just returns).
        '''
        # step 1: split the message into fragments of at most 31 bytes
        fragments = [msg[i:i + 31] for i in range(0, len(msg), 31)]

        # step 2: attach the header
        n = len(fragments)
        headers = [encoding if i < n - 1 else encoding + len(fragments[i]) << 3 for i in range(0, n)]

        # step 3: construct blocks
        blocks = [bytes([h]) + f + b'\x00' * (31 - len(f)) for h, f in zip(headers, fragments)]
        return blocks


    @classmethod
    def __encrypt(cls, blocks, k, IV):
        '''
        '''
        encrypted = []
        for i in range(0, len(blocks)):
            iv = (int.from_bytes(IV, 'big') + i).to_bytes(17, 'big')[-16:]
            cypher = AES.new(k, AES.MODE_CBC, iv)
            encrypted += [cypher.encrypt(blocks[i])]

        return encrypted


    def __send(self, address, blocks, sequence_number):
        '''
        '''
        for i in range(0, len(blocks)):
            sequence = str(sequence_number + i)
            builder = Builder(secret = self.__kp.seed().decode(), sequence = sequence)
            builder.append_payment_op(address, '0.0000001', 'XLM')
            builder.add_hash_memo(blocks[i])
            builder.sign()
            builder.submit()


    def Send(self, address, msg, encoding = 0):
        '''
        Send

        Args:
            address: This is the public Stellar address of your contact.
            message: The message (bytes) that you want to trasmit.

        Returns:
            The return value. True if sending was successful, False otherwise.
        '''

        # encode message
        encoded = Whisperer.__encode(msg, encoding)

        # encapsulate message
        blocks = Whisperer.__encapsulate(encoded, encoding)
        DumpBlocks(blocks)

        # calculate shared secret
        pk = ed25519_pk_to_curve25519_pk(decode_check('account', address))
        k = crypto_box_beforenm(pk, self.__sk)
        print('\nShared secret = {}'.format(base64.b16encode(k).decode()))

        # obtain the account sequence number
        sequence_number = int(horizon.account(self.__kp.address().decode()).get('sequence'))
        IV = (int.from_bytes(pk[0:16], 'big') + sequence_number).to_bytes(17, 'big')[-16:]
        print('Base IV = {}'.format(base64.b16encode(IV).decode()))

        # encrypt
        encrypted = Whisperer.__encrypt(blocks, k, IV)
        DumpEncrypted(encrypted)

        self.__send(address, encrypted, sequence_number)
