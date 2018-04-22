from stellar_base.address import Address
from stellar_base.keypair import Keypair
from stellar_base.utils import encode_check, decode_check
from stellar_base.horizon import horizon_testnet
from stellar_base.builder import Builder
from nacl.signing import SigningKey, VerifyKey
from nacl.bindings import crypto_box_beforenm
from Crypto.Cipher import AES
import base64
import pprint


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
        fb = blocks[i][1:]
        fa = ''.join([s if ord(s) < 127 and ord(s) > 31 else ' ' for s in fb.decode('ascii', errors='ignore')])
        print("{0}|{1}|{2} {3}".format(h[0:5], h[5:8], base64.b16encode(fb).decode(), fa))
    print('────────────────────────────────────────────────────────────────────────────────────────')


def DumpEncrypted(encrypted):
    '''
    '''
    print('\nEncrypted blocks')
    print('────────────────────────────────────────────────────────────────────────────────────────')
    for i in range(0, len(encrypted)):
       print("{}".format(base64.b16encode(encrypted[i]).decode()))
    print('────────────────────────────────────────────────────────────────────────────────────────')


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
        self.__sk = SigningKey(kp.raw_seed()).to_curve25519_private_key()._private_key
        self.__pk = VerifyKey(kp.raw_public_key()).to_curve25519_public_key()._public_key
        self.__address = kp.address().decode()
        self.__seed = kp.seed().decode()


    @classmethod
    def __addressToPk(cls, address):
        '''
        '''
        return VerifyKey(decode_check('account', address)).to_curve25519_public_key()._public_key


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
            The encoded message.
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
    def __encrypt(cls, blocks, k, baseIV):
        '''
        '''
        encrypted = []
        for i in range(0, len(blocks)):
            iv = (int.from_bytes(baseIV, 'big') + i).to_bytes(17, 'big')[-16:]
            cypher = AES.new(k, AES.MODE_CBC, iv)
            encrypted += [cypher.encrypt(blocks[i])]

        return encrypted


    @classmethod
    def __decrypt(cls, encrypted, k, IV):
        '''
        '''
        cypher = AES.new(k, AES.MODE_CBC, IV)
        decrypted = cypher.decrypt(encrypted)

        return decrypted


    @classmethod
    def __getLength(cls, block):
        '''
        __getLength

        Args:
            block: block containing an encapsulated message fragment

        Returns:
            The length of the encapsulated fragment.
        '''
        return block[0] >> 3


    @classmethod
    def __getEncoding(cls, block):
        '''
        __getEncoding

        Args:
            block: block containing an encapsulated message fragment

        Returns:
            The message fragment encoding format.
        '''
        return block[0] &  7


    def __send(self, address, blocks, sequence_number):
        '''
        '''
        for i in range(0, len(blocks)):
            sequence = str(sequence_number + i)
            builder = Builder(secret = self.__seed, sequence = sequence)
            builder.append_payment_op(address, '0.0000001', 'XLM')
            builder.add_hash_memo(blocks[i])
            builder.sign()
            builder.submit()


    def __shared(self, address):
        '''
        __shared

        Args:
            address: Stellar address of the counterparty.

        Returns:
            The shared secred according to ed25519.
        '''
        pk = Whisperer.__addressToPk(address)
        k = crypto_box_beforenm(pk, self.__sk)
        #print('\nShared secret = {}'.format(base64.b16encode(k).decode()))

        return k


    def Send(self, address, msg, encoding = 0):
        '''
        Send

        Args:
            address: This is the public Stellar address of your receiver.
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
        k = self.__shared(address)

        # obtain the account sequence number
        sequence_number = int(horizon.account(self.__address).get('sequence'))

        # build the IV
        pk = Whisperer.__addressToPk(address)
        IV = (int.from_bytes(pk[0:16], 'big') + sequence_number).to_bytes(17, 'big')[-16:]
        #print('Base IV = {}'.format(base64.b16encode(IV).decode()))

        # encrypt
        encrypted = Whisperer.__encrypt(blocks, k, IV)
        DumpEncrypted(encrypted)

        self.__send(address, encrypted, sequence_number)


    def Read(self, address, tail = 1, cursor = None):
        '''
        Read

        Args:
            address: This is the public Stellar address of the sender.
            tail: Read n = `tail` last messages.
            cursor:  Read all messages received after this sequence number.
        '''

        # Get all transactions
        tr = horizon.account_transactions(self.__address, params = {'order': 'desc', 'limit': 100}).get('_embedded').get('records')

        # filter out only transations from specified address and with memo type = hash
        tr = [t for t in tr if t.get('source_account') == address and t.get('memo_type') == 'hash']
        #pprint.pprint(tr)

        # calculate shared secret
        k = self.__shared(address)

        # decrypt memo blocks until a message is found
        messages = []
        nfound = 0
        for t in tr:
            # get the transaction sequence number
            sequence_number = int(t.get('source_account_sequence'))

            # build the IV and decrypt
            pk = Whisperer.__addressToPk(self.__address)
            IV = (int.from_bytes(pk[0:16], 'big') + sequence_number).to_bytes(17, 'big')[-16:]
            encrypted = base64.b64decode(t.get('memo'))
            block = Whisperer.__decrypt(encrypted, k, IV)

            # check if we have found the message
            l = Whisperer.__getLength(block)
            if l == 0:
                if len(messages) == 0:
                    continue
                messages[len(messages)-1].append(block[1:])
            if l > 0:
                nfound += 1
                if (nfound > tail):
                    break
                messages.append([block[1:(l+1)]])

        messages = [b''.join(reversed(m)) for m in messages]

        return messages
