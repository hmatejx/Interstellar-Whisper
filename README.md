# Interstellar Whisper

*Sending whispers across the interstellar space!*

This project holds the development of secure messaging over the distributed [Stellar](https://www.stellar.org) network.

## Introduction

Previous attempts at ubiquitous encryption, such as the *Web of trust* concepts of PGP/GPG, PKI, and DNSSEC have been (and to some extent still are) hampered by a lack of proper incentives. Security just isn't considered a must-have in the eyes of a typical user. For example, I still remember myself trying to use GPG with some discipline approximately 10 years ago, only to lose sync of the public keys of my contacts, and eventually losing my own keys at some point. I didn't even bother to recover them. I had nothing to loose. My interactions continued un-encrypted. Eventually, even the most enthusiastic of my contacts gave up.

On the other hand, the idea of public-key cryptography is essentially embedded into the concept of cryptocurrencies. In simplified terms, your public key (or sometimes a hash of it, as in the case of Bitcoin) is the *address*, to which you can send a coin, and your secret key (which you should really never tell anyone) is the *ticket* that allows you to spend the coins that you own.

One of the benefits of the rise, adoption, and proliferation of cryptocurrencies is that adopters are also necessarily (stake)holders of their cryptographic key pairs. As such, they have a direct monetary incentive to **never lose their keys**! Considering this, it becomes obvious that these exact same cryptographic keys could be further utilized and leveraged.

In this project I propose using cryptocurrency keys for highly secure, persistent, and resilient messaging. What features do we gain by sending messages over cryptocurrency networks?

- **Security:** strong encryption with no possibility man-in-the-middle attacks
- **Authenticity**: message authenticity is guaranteed by the rules of the network
- **Resilience:** the network is decentralized, no single node to attack, making sending messages difficult to block (the only option is to completely block the client from the network)
- **Persistency:** the history is immutable, distributed, and protected by the consensus protocol, which allows retrieving messages at any point in the future
- **Plausible deniability:** some protocols already contain optional fields for hashes which are indistinguishable from encrypted messages

A break of any of the above would at the same time mean a break of the underlying cryptography, *breaking the network itself*. As such, cryptocurrencies will continue to evolve towards more secure algorithms when security margin become too low.

## Using the distributed Stellar network as a vehicle for transporting messages

From the various cryptocurrencies that I am familiar with, I could not find a better candidate than Stellar (XLM) for this project. 

Stellar has one of the best [developer ecosystems](https://www.stellar.org/developers/) that I have looked at. There are official SDK libraries available for Java, JavaScript, and Go with excellent documentation. Further community SDKs for Python, Ruby, Go, C#, and C++ are also available. Transactions are also very fast (resolve in 2 - 5 seconds) and cheap (100 stroops ~ 0.000003 USD at the time of writing). Decentralization and the size of the network continue to increase and there is currently no end in sight. But the most important criterion is, in my opinion, the open-mindedness of the [Stellar Development Foundation](www.stellar.org).

## Proposed protocol



## Proof of concept

**TODO: this below is the old approach using the ```libsodium``` functions**

Bob wants to send a message to Alice. Bob and Alice are both users of the Stellar network, and have their public keys published within the distributed ledger. 

Since they also both own their respective secret keys, this allows Bob to send Alice a message using public key cryptography. Specifically the Sealed Box concept is relevant here as it provides encryption with an ephemeral key which cannot be recovered by Bob. The Alice is the only person that can now decipher the received message.

The message itself is sent in chunks using the ```MEMO_HASH``` field of the Stellar transaction (providing 32 bytes of transport spate for packet fragmentation).

Below is a test showing Bob submitting a secret message to Alice.

```
$ python3 bob.py 
[Message for Alice]─────────────────────────────────────────────────────
Hello world!
[END Message]───────────────────────────────────────────────────────────
```

Alice can indeed decrypt the message.

```
$ python3 alice.py 
[Message from Bob]──────────────────────────────────────────────────────
Hello world!
[END Message]───────────────────────────────────────────────────────────
```

The two fragments of the above transaction can be seen on Stellar test-net:

http://testnet.stellarchain.io/tx/7722aa6ebf4e6fb47a8b0d33ad025173f7e1753f7252cf8c5372e7b0dfaafeb5

http://testnet.stellarchain.io/tx/53f75829261447ef4a1ee581649d7301a5938bfbc8df290fc16a4e66139fee51

