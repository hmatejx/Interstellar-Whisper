#!/usr/bin/python3

# required in case the TestNet gets reset
import requests
from stellar_base.keypair import Keypair


seed =['SC7G2Y4DAGF3ARCEDGYYW4CR7E3RSOCDHMOLRRWOOWSIUILIOED6DLDV', 'SDVYV44C63H4S6W4FT4SBNML3C4YNUA75Z4DZBDP6OBBEZUREBMP3KIP']
kp = [Keypair.from_seed(s) for s in seed]
pubk = [k.address().decode() for k in kp]

url = 'https://friendbot.stellar.org'
for addr in pubk:
    r = requests.get(url, params={'addr': addr})
