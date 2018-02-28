# stellar-base
from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.utils import encode_check
# PyNaCl
from nacl.public import PrivateKey, PublicKey
from nacl.signing import SigningKey, VerifyKey
# misc
import base64
import json
import requests


def print_json(obj):
    print(json.dumps(obj, default=lambda x: x.__dict__))


def CurveKeyPair(kp):
    sk = PrivateKey(SigningKey(kp.raw_seed()).to_curve25519_private_key()._private_key)
    pk = PublicKey(VerifyKey(kp.raw_public_key()).to_curve25519_public_key()._public_key)

    return sk, pk


def CurvePrivateKey(kp):
    return  PrivateKey(SigningKey(kp.raw_seed()).to_curve25519_private_key()._private_key)


def CurvePublicKey(kp):
    return PublicKey(VerifyKey(kp.raw_public_key()).to_curve25519_public_key()._public_key)


def info_kp(kp, name):
    print("\n┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓")
    print("┃ Keypair information for {:14} ┃".format(name))
    print("┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛")

    print("\nStellar format")
    print("────────────────────────────────────────────────────────────────────────────────────────")
    print("Secret key (SEED)     \t{}".format(encode_check('seed', kp.raw_seed()).decode()))
    print("Public key (ADDRESS)  \t{}".format(encode_check('account', kp.raw_public_key()).decode()))

    print("\n ⇨ Ed25519 keypair")
    print("────────────────────────────────────────────────────────────────────────────────────────")
    print("Secret key            \t{}".format(base64.b16encode(kp.raw_seed()).decode()))
    print("Public key            \t{}".format(base64.b16encode(kp.raw_public_key()).decode()))

    sk, pk = CurveKeyPair(kp)
    print("\n ⇨ Curve25519 keypair")
    print("────────────────────────────────────────────────────────────────────────────────────────")
    print("Secret key            \t{}".format(base64.b16encode(sk._private_key).decode()))
    print("Public key            \t{}".format(base64.b16encode(pk._public_key).decode()))


def create_address(kp):
    publickey = kp.address().decode()
    url = 'https://horizon-testnet.stellar.org/friendbot'
    r = requests.get(url, params={'addr': publickey})

    print(r.status_code)


def check_account(addr):
    address = Address(addr)
    address.get()

    print_json(address)