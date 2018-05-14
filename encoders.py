import lib.smaz
from bitstring import BitArray, BitStream

__all__ = ['EncodeGSM', 'DecodeGSM', 'EncodeSixbit', 'DecodeSixbit', 'Compress', 'Decompress']


# lookup constant strings for the encodings
__gsm = ("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
         "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà")
__sixbit = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_ !\"#$%&'()*+,-./0123456789:;<=>?"


def EncodeGSM(txt):
    '''
    Encode the text string (provided as byte array) into
    the GSM 03.38 character set. Extended characters are
    not supported. Unsupported characters are mapped into
    blank spaces.

    Args:
        txt: The original text as UTF-8 encoded byte array.

    Returns:
        The encoded text as byte array.
    '''
    # ugly hack using binary strings
    res = ''

    for c in txt.decode('utf-8', errors = 'ignore'):
        idx = __gsm.find(c)
        if idx != -1:
            res += '{:07b}'.format(idx)
        else:
            res += '0100000'

    # zero pad the last byte if necessary
    lastbits = len(res) % 8
    if lastbits > 0:
        res += '0' * (8 - lastbits)

    return BitArray('0b' + res).bytes


def DecodeGSM(gsm):
    '''
    Decode the encoded message from the GSM 03.38 character set.

    Args:
        gsm: The GSM 03.38 encoded text as byte array.

    Returns:
        The decoded text as UTF-8 encoded byte array.
    '''
    # convert to bit stream
    bits = BitStream(gsm)

    # get the indices, characters, and merge together
    res = ''.join(__gsm[idx] for idx in bits.readlist('{}'.format(len(bits) // 7) + '*uint:7')).encode('utf-8')

    # strip last character in case we have a perfect wrapping
    if len(bits) % 7 == 0 and chr(res[-1]):
        res = res[0:len(res) - 1]

    return res


def EncodeSixbit(txt):
    '''
    Encode the text string (provided as byte array) into
    the AIS Sixbit ASCII character set. Unsupported characters
    are mapped into blank spaces.

    Args:
        txt: The original text encoded as UTF-8 byte array.

    Returns:
        The encoded text as byte array.
    '''
    # ugly hack using binary strings
    res = ''

    for c in txt.decode('utf-8', errors = 'ignore').upper():
        idx = __sixbit.find(c)
        if idx != -1:
            res += '{:06b}'.format(idx)
        else:
            res += '100000'

    # zero pad the last byte if necessary
    lastbits = len(res) % 8
    if lastbits > 0:
        res += '0' * (8 - lastbits)

    return BitArray('0b' + res).bytes


def DecodeSixbit(six):
    '''
    Decode the encoded message from the AIS Sixbit ASCII character set.

    Args:
        six: The AIS Sixbit encoded text as byte array.

    Returns:
        The decoded text as UTF-8 encoded byte array.
    '''
    # convert to bit stream
    bits = BitStream(six)

    # get the indices, characters, and merge together
    res = ''.join(__sixbit[idx] for idx in bits.readlist('{}'.format(len(bits) // 6) + '*uint:6')).encode('utf-8')

    # strip last character in case we have a perfect wrapping
    if len(bits) % 6 == 0 and chr(res[-1]):
        res = res[0:len(res) - 1]

    return res


def Compress(txt):
    '''
    Compress the text message (provided as byte array).
    The text will first be coerced to ASCII, as the SMAZ
    compression algorithm can only process ASCII strings.

    Args:
        txt: The original message encoded as UFT-8 byte array.

    Returns:
        The smaz compressed text as byte array.
    '''
    return lib.smaz.compress(txt.decode('ascii', errors = 'ignore')).encode('utf-8')


def Decompress(comp):
    '''
    decompress the SMAZ compressed byte array.

    Args:
        txt: The message to be compressed as byte array.

    Returns:
        The smaz compressed text as UTF-8 encoded byte array.
    '''
    return lib.smaz.decompress(comp.decode('utf-8')).encode('utf-8')


if __name__ == '__main__':

    m = "This is a test like Lorem Ipsum".encode('utf-8')

    # Test GSM 03.38
    print('\nGSM 03.38 Encoding test')
    e = EncodeGSM(m)
    d = DecodeGSM(e)
    print(' - Original message: "{}"   length = {}'.format(m.decode('utf-8'), len(m)))
    print(' - Encoded message:  "{}"   length = {}'.format(e, len(e)))
    print(' - Decoded message:  "{}"   length = {}'.format(d.decode('utf-8'), len(d)))
    assert m == d

    # Test Sixbit ASCII
    print('\nSixbit ASCII Encoding test')
    e = EncodeSixbit(m)
    d = DecodeSixbit(e)
    print(' - Original message: "{}"   length = {}'.format(m.decode('utf-8'), len(m)))
    print(' - Encoded message:  "{}"   length = {}'.format(e, len(e)))
    print(' - Decoded message:  "{}"   length = {}'.format(d.decode('utf-8'), len(d)))
    assert m.upper() == d

    # smaz compression
    print('\nSmaz Compression test')
    e = Compress(m)
    d = Decompress(e)
    print(' - Original message: "{}"   length = {}'.format(m.decode('utf-8'), len(m)))
    print(' - Encoded message:  "{}"   length = {}'.format(e, len(e)))
    print(' - Decoded message:  "{}"   length = {}'.format(d.decode('utf-8'), len(d)))
    assert m == d
