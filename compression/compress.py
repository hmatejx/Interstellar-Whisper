import lib.smaz
import pyshoco

# read the SMS "corpus"
sms = [line.rstrip('\n') for line in open('sms.txt')]

i = 1
for txt in sms:
    c1 = lib.smaz.compress(txt)
    c2 = pyshoco.compress(txt)
    cr = min((len(c1), len(c2)))

    print("Message {}, size = {}, smaz = {}{}, shoco = {}{}, rate = {:.3}%".format(
        i,
        len(txt),
        '*' if len(c1) <= len(c2) else ' ',
        len(c1),
        '*' if len(c1) > len(c2) else ' ',
        len(c2),
        100*cr/len(txt)
        ))

    i = i + 1

