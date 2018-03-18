# Interstellar Whisper

*Sending whispers across the interstellar space!*

![](img/stars.jpg)

This project holds the development of covert  messaging over the distributed [Stellar](https://www.stellar.org) network.

## Introduction

Previous attempts at ubiquitous encryption, such as the *Web of trust* concepts of PGP/GPG, PKI, and DNSSEC have been (and to some extent still are) hampered by a lack of proper incentives. Security just isn't considered a must-have in the eyes of a typical user. 

For example, I still remember myself trying to use GPG with some discipline approximately 10 years ago, only to lose sync of the public keys of my contacts, and eventually losing my own keys at some point. I didn't even bother to recover them. I had nothing to loose. My interactions continued un-encrypted. Eventually, even the most enthusiastic of my contacts gave up.

On the other hand, the idea of public-key cryptography is essentially embedded into the concept of cryptocurrencies. In simplified terms, your public key (or sometimes a hash of it, as in the case of Bitcoin) is the *address*, to which you can send a coin, and your secret key (which you should really never tell anyone) is the *ticket* that allows you to spend the coins that you own.

One of the benefits of the rise, adoption, and proliferation of cryptocurrencies is that adopters are also necessarily (stake)holders of their cryptographic key pairs. As such, they have a direct monetary incentive to **never lose their keys**! Considering this, it becomes obvious that these exact same cryptographic keys could be further utilized and leveraged.

In this project I propose using cryptocurrency keys for highly secure, persistent, and resilient messaging. What features do we gain by sending messages over cryptocurrency networks?

- **Security:** strong encryption with no possibility of man-in-the-middle attacks.
- **Authenticity**: message authenticity is guaranteed by the rules of the network.
- **Resilience:** the network is decentralized, no single node to attack, making sending messages difficult to block (the only option is to completely block the client from the network).
- **Persistency:** the history is immutable, distributed, and protected by the consensus protocol, which allows retrieving messages at any point in the future.
- **Plausible deniability:** some protocols contain optional fields for hashes which are indistinguishable from encrypted messages and the sender himself cannot decode the sent messages if ephemeral key pairs were used.

A break of any of the above would at the same time mean a break of the underlying cryptography, *breaking the network itself*. As such, cryptocurrencies will continue to evolve towards more secure algorithms when security margin become too low.

## Using the distributed Stellar network as a vehicle for transporting messages

From the various cryptocurrencies that I am familiar with, I could not find a better candidate than Stellar (XLM) for this project. 

Stellar has one of the best [developer ecosystems](https://www.stellar.org/developers/) that I have looked at. There are official SDK libraries available for [Java](https://github.com/stellar/java-stellar-sdk), [JavaScript](https://www.stellar.org/developers/js-stellar-sdk/reference/), [Ruby](https://github.com/stellar/ruby-stellar-sdk) and [Go](https://github.com/stellar/go) with excellent documentation. Further community SDKs for [Python](https://github.com/StellarCN/py-stellar-base), [C#](https://github.com/QuantozTechnology/csharp-stellar-base), and [C++](https://github.com/bnogalm/StellarQtSDK) are also available. 

Transactions are also very fast (resolve in 2 - 5 seconds) and cheap (100 stroops ~ 0.000003 USD at the time of writing). Decentralization and the size of the network continue to increase and there is currently no end in sight. But the most important criterion is, in my opinion, the open-mindedness of the [Stellar Development Foundation](www.stellar.org).

## Proposed protocol

Prior to messaging, Alice and Bob convert their Ed25519 Elliptic Curve keys, corresponding to Stellar's private seed and public address, to Curve25519 keys which will allow them to perform Elliptic Curve Diffie-Hellman exchange according to the rules of X25519.

Let's call these Curve25519 keys `sk_Bob, pk_Bob, sk_Alice, and pk_Alice`.

**Scenario:** Bob sends a message to Alice

#### Step 1: Diffie-Hellman

Bob's calculates the shared secret by using his secret key and Alice's public key using the `ECDH` algorithm. Alice does the same calculation using her secret key and Bob's public key.  Let's call this shared 256-bit secret value `k`, 

```
k = ECDH(pk_Alice, sk_Bob) = ECDH(pk_Bob, sk_Alice)
```

#### Step 2: Message encapsulation

The encapsulation is easiest to describe on an example. Imagine wanting to transmit a 46 byte long payload. The payload itself is a suitably *encoded* plaintext message or a small file that Bob wants to transmit  (more information on encoding is provided Step 3 below).

```
|0                  |10                 |20                 |30                 |40
|0 1 2 3 4 5 6 7 8 9|0 1 2 3 4 5 6 7 8 9|0 1 2 3 4 5 6 7 8 9|0 1 2 3 4 5 6 7 8 9|0 1 2 3 4 5 6
┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
| Payload                                                                            46 bytes |
└─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
```

1. The first step of encapsulation is to split the payload into fragments of maximum length of 31 bytes, resulting in two fragments of lengths of 31 and 15.

       |0                  |10                 |20                 |30 
       |0 1 2 3 4 5 6 7 8 9|0 1 2 3 4 5 6 7 8 0|1 2 3 4 5 6 7 8 9 0|1
       ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
       | Fragment 1                                         31 bytes |
       └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
       ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
       | Fragment 2           15 bytes |
       └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘

2. Next, a 1 byte header `H` is attached to each fragment

       |0                  |10                 |20                 |30 
       |0 1 2 3 4 5 6 7 8 9|0 1 2 3 4 5 6 7 8 0|1 2 3 4 5 6 7 8 9 0|1 2
       ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
       |H| Fragment 1                                1 + 31 = 32 bytes |
       └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘
       ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐
       |H| Fragment 2  1 + 15 = 16 bytes |
       └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘

  The 8 bits of the header depend on the *length* `L` of the fragment (bits 1 - 5) and on the *encoding* `E` of the payload (bits 6 - 8). The first 5 bits of the header encode the fragment length:

  | Length (L) | Header bits     | Description                                                |
  | ---------- | --------------- | ---------------------------------------------------------- |
  | 1 ... 31   | 00001 ... 11111 | Last fragment of the payload of size L                     |
  | 0          | 00000           | Full size fragment, payload continues in the next fragment |

  The next 3 bits of the header encode the encoding:

  | Encoding | Header bits | Description |
  | -------- | ----------- | ----------- |
  | 0        | 000         |             |
  | 1        | 001         |             |
  | 2        | 010         |             |
  | 3        | 011         |             |
  | 4        | 100         |             |
  | 5        | 101         |             |
  | 6        | 110         |             |
  | 7        | 111         |             |


#### Step 3: Encryption

- Let's call `x` the padded and encapsulated payload (i.e plaintext).

- The initiation vector (nonce) is given by

        IV = hash(sequence_number || pk_Bob || pk_Alice)

    where `sequence_number` is the sequential and increasing number attached to each transaction of a given Stellar address. The operator `||` above stands for string concatenation. 
    This construction assures that `IV` is always unique. For example, if Alice want's to send a message to bob, the order of public keys must be reversed. Even if Alice sends Bob the exact same plaintext message with an equal sequence number (the sequence number is only guaranteed to be unique for each address separately), the `IV` will still be different.

    The encrypted payload will then be

        c = AES(x, IV, k)

- *Optional:* It is also possible to chain multiple encryptions (even though I don't think that is necessary, AES should provide plenty of security margin). In this case we need to extend the 256-bit shared secret to more, e.g. 512, bits using a suitable Key Derivation Function

        k1 || k2 = KDF(k)

    The first encryption round (using AES-256) is then

        c' = AES(x, IV, k1)

    and the second encryption round (for example, using Twofish)

        c = Twofish(c', IV, k2)



#### Step 4: Sending the message

The final encrypted message `c` is set as the 32 byte `MEMO_HASH` field of the Stellar transaction object. A payment transaction is constructed (e.g. using the 0.0000001 XLM minimum amount). The total cost in this case will be 0.00000101 XLM per message block (the total cost is the sum of the transaction fee and the payment amount).

#### Step 5: Decryption

Perform the respective inverse operations as during encryption.

## Proof of concept

**TODO: this below is the old approach using the `libsodium` functions**

Bob wants to send a message to Alice. Bob and Alice are both users of the Stellar network, and have their public keys published within the distributed ledger. 

Since they also both own their respective secret keys, this allows Bob to send Alice a message using public key cryptography. Specifically the Sealed Box concept is relevant here as it provides encryption with an ephemeral key which cannot be recovered by Bob. The Alice is the only person that can now decipher the received message.

The message itself is sent in chunks using the `MEMO_HASH` field of the Stellar transaction (providing 32 bytes of transport spate for packet fragmentation).

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

## TODO
Think about a suitable hash for IV generation, suitable KDF for key extension in case of chaining multiple encryptions, and in general think carefully about the security of the above 'roll-your-own' crypto... **this is always a VERY bad thing to do!**