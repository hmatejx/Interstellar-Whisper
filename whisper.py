from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.utils import encode_check, decode_check
from nacl.signing import SigningKey, VerifyKey
from nacl.bindings import crypto_box_beforenm
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
import base64
#import json
#import requests


class Whisperer:
    def __init__(self, kp):
        """
        Initialize the Whisper class using your Stellar.

        Args:
            kp: This is your Stellar keypair, as encoded by the
                stellar_base.keypair class.

        Returns:
            Instance of the object.
        """
        self.__kp = kp
        self.__sk = Whisperer._ed25519_sk_to_curve25519_pk(kp.raw_seed())
        self.__pk = Whisperer._ed25519_pk_to_curve25519_pk(kp.raw_public_key())

    @classmethod
    def _ed25519_pk_to_curve25519_pk(cls, pk):
        return VerifyKey(pk).to_curve25519_public_key()._public_key

    @classmethod
    def _ed25519_sk_to_curve25519_pk(cls, sk):
        return SigningKey(sk).to_curve25519_private_key()._private_key

    def Send(self, address, message):
        """
        Send

        Args:
            address: This is the public Stellar address of your contact.
            message: The message (bytes) that you want to trasmit.

        Returns:
            The return value. True if sending was successful, False otherwise.
        """

        # shared secret key
        pk = Whisperer._ed25519_pk_to_curve25519_pk(decode_check('account', address))
        k = crypto_box_beforenm(pk, self.__sk)

        # nonce
        sequence_number = 26509955490119684 # temp
        # IV = (int.from_bytes(SHA256.new(self.__pk + pk ).digest()[0:16], 'big') + sequence_number).to_bytes(16, 'big')
        IV = (int.from_bytes(self.__pk[0:4] + pk[0:4] + b'\0'*8, 'big') + sequence_number).to_bytes(16, 'big')
        print(IV)
        # dump
        print("Shared secret = {}".format(base64.b16encode(k).decode()))
        print("IV = {}".format(base64.b16encode(IV).decode()))
