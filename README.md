# SubStellar

Secret and Secure messaging over the Stellar protocol using plausibly deniable encryption.

### Proof of concept

Bob wants to send a message to Alice. Bob and Alice are both users of the Stellar network, and have their public keys published within the distributed ledger. 

Since they also both own their respective secret keys, this allows Bob to send Alice a message using public key cryptography. Specifically the Sealed Box concept is relevant here as it provides encryption with an ephemeral key which cannot be recovered by Bob. The Alice is the only person that can now decipher the received message.

The message itself is sent in chunks using the ```MEMO_HASH``` field of the Stellar transaction (providing 32 bytes of transport spate for packet fragmentation).

Below is a test showing Bob submitting a secret message to Alice.

```matej@LxLe-develop:~/devel/test$ python3 bob.py 
$ python3 bob.py 
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Message for Alice!                                                  ┃
┗━BEGIN━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
Hello world!
━━END━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Alice can indeed decrypt the message.

```
$ python3 alice.py 
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Message from Bob!                                                   ┃
┗━BEGIN━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
Hello world!
━━END━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The two fragments of the above transaction can be seen on Stellar testnet:

http://testnet.stellarchain.io/tx/7722aa6ebf4e6fb47a8b0d33ad025173f7e1753f7252cf8c5372e7b0dfaafeb5

http://testnet.stellarchain.io/tx/53f75829261447ef4a1ee581649d7301a5938bfbc8df290fc16a4e66139fee51