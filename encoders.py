import lib.smaz
from bitstring import BitArray, BitStream

__all__ = ['EncodeGSM', 'DecodeGSM', 'EncodeSixbit', 'DecodeSixbit', 'Compress', 'Decompress']


__gsm = ("@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&'()*+,-./0123456789:;<=>?"
         "¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà")


def EncodeGSM(txt):
    '''
    '''
    # ugly hack using binary strings
    res = ''

    # find each character in the GSM 03.38 set
    # if you find it, take the index, otherwise
    # replace by the blank space character
    for c in txt.decode('utf-8', errors = 'ignore'):
        idx = __gsm.find(c)
        if idx != -1:
            res += '{:07b}'.format(idx)
        else:
            res.append('0100000')

    # zero pad the last byte if necessary
    lastbits = len(res) % 8
    if lastbits > 0:
        res += '0' * (8 - lastbits)

    return BitArray('0b' + res).bytes


def DecodeGSM(gsm):
    '''
    '''
    # convert to bit stream
    bits = BitStream(gsm)

    # get the indices, characters, and merge together
    res = ''.join(__gsm[idx] for idx in bits.readlist('{}'.format(len(bits) // 7) + '*uint:7')).encode('utf-8')

    return res


def EncodeSixbit(txt):
    '''
    '''
    return txt


def DecodeSixbit(six):
    '''
    '''
    return six


def Compress(txt):
    '''
    '''
    return txt


def Decompress(comp):
    '''
    '''
    return comp


if __name__ == '__main__':

    m = "This is a test like Lorem Ipsum...."
    e = EncodeGSM(m)
    d = DecodeGSM(e)

    print('Encoded message = {}, length = {}'.format(e, len(e)))
    print('Original message = {}, length = {}'.format(m, len(m)))
    print('Decoded message = {}, length = {}'.format(d, len(d)))

    assert m == d
