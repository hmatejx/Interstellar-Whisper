import lib.smaz
import pyshoco

# read the SMS "corpus"
sms = [line.rstrip('\n') for line in open('sms.txt')]

i = 1
print("message,size,smaz,shoco")
for txt in sms:
    c1 = lib.smaz.compress(txt)
    c2 = pyshoco.compress(txt)
    print("{},{},{},{}".format(i, len(txt), len(c1), len(c2)))
    i = i + 1
