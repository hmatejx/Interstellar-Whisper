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
from encoders import *


__all__ = ['Whisperer']


# This creates a new Horizon Livenet instance
horizon = horizon_testnet()

# Set to non-zero for debugging
DEBUG = 0


def DumpBlocks(blocks):
    '''
    Dumps the message blocks (encapsulated & encoded message fragments).
    For each block, the dump shows the header bits, the encoding bits,
    and the message fragment in hexadecimal to the standard output.

    Args:
        blocks: This is the list of message blocks.

    Returns:
        None.
    '''
    print('\nMessage blocks')
    print('────────────────────────────────────────────────────────────────────────────────────────')
    for i in range(0, len(blocks)):
        h = bin(blocks[i][0])[2:]
        h = '0' * (8 - len(h)) + h
        fb = blocks[i][1:]
        fa = Printable(fb)
        print('{0}|{1}|{2} {3}'.format(h[0:5], h[5:8], base64.b16encode(fb).decode(), fa))
    print('────────────────────────────────────────────────────────────────────────────────────────')


def DumpEncrypted(encrypted):
    '''
    Dumps the encripted 32 byte blocks in hexadecimal to the standard output.

    Args:
        encrypted: The list of encrypted blocks.

    Returns:
        None.
    '''
    print('\nEncrypted blocks')
    print('────────────────────────────────────────────────────────────────────────────────────────')
    for i in range(0, len(encrypted)):
       print('{}'.format(base64.b16encode(encrypted[i]).decode()))
    print('────────────────────────────────────────────────────────────────────────────────────────')


def Printable(msg):
    '''
    Converts the message given as byte array to printable form.
    All characters below 32 and above 126 are converted to blank spaces.

    Args:
        msg: The message to be converted to printable characters.

    Returns:
        Byte array containing the printable characters from the message.
    '''
    return ''.join([s if ord(s) < 127 and ord(s) > 31 else ' ' for s in msg.decode('utf-8', errors='ignore')]).encode('utf-8')


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
        Transform the stellar address (encoded ed25519 public key)
        to the coresponding curve25519 public key.

        Args:
            address: This is your Stellar address starting with letter 'G'.

        Returns:
            curve25519 public key as byte array.
        '''
        return VerifyKey(decode_check('account', address)).to_curve25519_public_key()._public_key


    @classmethod
    def __encode(cls, msg, enc):
        '''
        Encode the message using the required encoding,
        potentially save some precious space.

        Args:
            mgs: The message to be encoded as byte array.
            enc: The desired encoding.

        Returns:
            The encoded message as byte array.
        '''
        # raw bytes, no encoding
        if enc == 0:
            return msg

        # SMS TEXT encoding, not implemented yet
        if enc == 1:
            return EncodeGSM(msg)

        # Sixbit ASCII, not implemented yet
        if enc == 2:
            return EncodeSixbit(msg)

        # not implemented yet
        if enc == 3:
            return Compress(msg)

        # reserved, not implemented
        if enc == 4:
            return msg

        # reserved, not implemented
        if enc == 5:
            return msg

        # reserved, not implemented
        if enc == 6:
            return msg

        # reserved, not implemented
        if enc == 7:
            return msg

        print('\nError: wrong encoding {} specified!'.format(enc))
        return None


    @classmethod
    def __decode(cls, msg, enc, printable):
        '''
        Decode the message using the provided encoding.

        Args:
            mgs: The encoded message as byte array.
            enc: The respective encoding used.

        Returns:
            The decoded message as byte array.
        '''

        # raw bytes, no encoding
        if enc == 0:
            if printable:
                return Printable(msg)
            return msg

        # SMS TEXT encoding, not implemented yet
        if enc == 1:
            return DecodeGSM(msg)

        # Sixbit ASCII, not implemented yet
        if enc == 2:
            return DecodeSixbit(msg)

        # not implemented yet
        if enc == 3:
            return Decompress(msg)

        # reserved, not implemented
        if enc == 4:
            if printable:
                return Printable(msg)
            return msg

        # reserved, not implemented
        if enc == 5:
            if printable:
                return Printable(msg)
            return msg

        # reserved, not implemented
        if enc == 6:
            if printable:
                return Printable(msg)
            return msg

        # reserved, not implemented
        if enc == 7:
            if printable:
                return Printable(msg)
            return msg

        print('Error: wrong encoding {} specified!'.format(enc))
        return None


    @classmethod
    def __encapsulate(cls, msg, encoding):
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
        headers = [encoding if i < n - 1 else encoding + (len(fragments[i]) << 3) for i in range(0, n)]

        # step 3: construct blocks
        blocks = [bytes([h]) + f + b'\x00' * (31 - len(f)) for h, f in zip(headers, fragments)]
        return blocks


    @classmethod
    def __encrypt(cls, blocks, k, baseIV):
        '''
        Encrypt the message blocks using the provided shared secret
        and initialization vector sequence start.

        Args:
            k: The shared secret.
            baseIV: The initialization vector for encrypting the first block.

        Returns:
            List of encrypted message blocks (byte arrays).
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
        Decrypt the single message block using the provided
        shared secret and initialization vector.

        Args:
            k: The shared secret.
            IV: The initialization vector.
        '''
        cypher = AES.new(k, AES.MODE_CBC, IV)
        decrypted = cypher.decrypt(encrypted)

        return decrypted


    @classmethod
    def __getLength(cls, block):
        '''
        Return the length of fragment encapsulated in the block.

        Args:
            block: block containing an encapsulated message fragment

        Returns:
            The length of the encapsulated fragment as integer.
        '''
        return block[0] >> 3


    @classmethod
    def __getEncoding(cls, block):
        '''
        Return the encoding of fragment encapsulated in the block.

        Args:
            block: block containing an encapsulated message fragment

        Returns:
            The encoding of the message fragment as integer.
        '''
        return block[0] &  7


    def __send(self, address, encrypted, sequence_number):
        '''
        Sends the encrypted blocks to the recipient as sequential
        payment transactions.

        Args:
            address: The Stellar address of the recipient.
            encrypted: The encrypted message blocks.
            sequence_number: The current sequence number of the
                             sending account.

        Returns:
            True if successful, False otherwise.
        '''
        try:
            for i in range(0, len(encrypted)):
                sequence = str(sequence_number + i)
                builder = Builder(secret = self.__seed, sequence = sequence)
                builder.append_payment_op(address, '0.0000001', 'XLM')
                builder.add_hash_memo(encrypted[i])
                builder.sign()
                builder.submit()
        except:
            return False

        # todo: check sending status
        return True


    def __shared(self, address):
        '''
        Calculate the shared secret according to X25519.

        Args:
            address: Stellar address of the counterparty.

        Returns:
            The shared secred according to X25519 as byte array.
        '''
        # convert the recipient public address to curve25519 public key
        pk = Whisperer.__addressToPk(address)

        # calculate the shared secret according to X25519
        k = crypto_box_beforenm(pk, self.__sk)
        if DEBUG:
            print('\nShared secret = {}'.format(base64.b16encode(k).decode()))

        return k


    def Send(self, address, msg, encoding):
        '''
        Send the message to the Stellar address using the requested
        encoding.

        Args:
            address: This is the public Stellar address of your receiver.
            msg: The message (byte array) that you want to transmit.
            encoding: The encoding to use for the message.

        Returns:
            The return value. True if sending was successful, False otherwise.
        '''

        if address == self.__address:
            print('\nError: sending to yourself is not yet supported!')
            return False

        # encode message
        encoded = Whisperer.__encode(msg, encoding)

        print(encoded)

        # encapsulate message
        blocks = Whisperer.__encapsulate(encoded, encoding)
        if DEBUG:
            DumpBlocks(blocks)

        # calculate shared secret
        k = self.__shared(address)

        # obtain the account sequence number
        sequence_number = int(horizon.account(self.__address).get('sequence'))

        # build the IV
        pk = Whisperer.__addressToPk(address)
        IV = (int.from_bytes(pk[0:16], 'big') + sequence_number).to_bytes(17, 'big')[-16:]
        if DEBUG:
            print('Base IV = {}'.format(base64.b16encode(IV).decode()))

        # encrypt
        encrypted = Whisperer.__encrypt(blocks, k, IV)
        if DEBUG:
            DumpEncrypted(encrypted)

        # actually perform the sending of the encrypted blocks
        return self.__send(address, encrypted, sequence_number)


    def Read(self, address = None, tail = 1, cursor = None, printable = False):
        '''
        Read the last `tail` received messages. The function will:
        - Iterate through the received payment operations with the hash
          memo type field populated in the reverse order, starting with
          the last.
        - Decrypt the encrypted blocks one after another using the
          (deterministic) shared secret and IV.
        - Check which blocks fit together by considering the length field
          as a separator (the last block with non-zero length header field
          marks the start of the preceding message).

        Args:
            address: This is the public Stellar address of the sender.
            tail: Read n = `tail` last messages.
            cursor: Read all messages received after this sequence number.
            printable:

        Returns:
            The secret messages.
        '''

        # Get all transactions
        tr = horizon.account_transactions(self.__address, params = {'order': 'desc', 'limit': 100}).get('_embedded').get('records')

        if DEBUG > 1:
            pprint.pprint(tr)

        # filter out only transations from specified address and with memo type = hash
        tr = [t for t in tr if (t.get('source_account') == address or address is None) \
                                and t.get('source_account') != self.__address \
                                and t.get('memo_type') == 'hash']

        # decrypt memo blocks until a message is found
        messages = []
        encodings = []
        sender = []
        dates = []
        nfound = 0
        for t in tr:
            # get the transaction source address
            address = t.get('source_account')

            # calcul01ate shared secret
            k = self.__shared(address)

            # get sequence number
            sequence_number = int(t.get('source_account_sequence')) - 1

            # build the IV and decrypt
            pk = Whisperer.__addressToPk(self.__address)
            IV = (int.from_bytes(pk[0:16], 'big') + sequence_number).to_bytes(17, 'big')[-16:]
            encrypted = base64.b64decode(t.get('memo'))
            block = Whisperer.__decrypt(encrypted, k, IV)

            if DEBUG:
                DumpBlocks([block])

            # check if we have found the message
            l = Whisperer.__getLength(block)
            # this is not the last block of a message
            if l == 0:
                # either we have not yet found the last message
                if len(messages) == 0:
                    continue
                # or this is a block of the current message
                messages[len(messages)-1].append(block[1:])
            # we found a new message
            if l > 0:
                nfound += 1
                # we already found enough messages
                if (nfound > tail):
                    break
                messages.append([block[1:(l + 1)]])
                encodings.append(Whisperer.__getEncoding(block))
                sender.append(t.get('source_account'))
                dates.append(t.get('created_at'))

        if DEBUG:
            print(encodings)

        # assemble the encoded messages
        messages = [b''.join(reversed(m)) for m in messages]

        # decode the messages
        messages = [Whisperer.__decode(messages[i], encodings[i], printable) for i in range(0, len(messages))]

        return [[dates[i], sender[i], messages[i]] for i in range(0, len(messages))]


    @classmethod
    def ValidateAddress(cls, address):
        '''
        Validate the given Stellar address.

        Args:
            address: The public address of a Stellar account.

        Return:
            True if public address is valid, False otherwise.
        '''
        try:
            decode_check('account', address)
            return True
        except:
            return False


    @classmethod
    def ValidateSeed(cls, seed):
        '''
        Validate the given private Stellar key.

        Args:
            seed: The private key of a Stellar account.

        Return:
            True if the secret key is valid, False otherwise.
        '''
        return decode_check('seed', seed)
