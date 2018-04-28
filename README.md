# Interstellar Whisper

*Sending whispers across the interstellar space!*

![stellar rocket in space](img/stars.jpg)

This [project](https://github.com/hmatejx/Interstellar-Whisper/) holds the development of encrypted messaging over the distributed [Stellar](https://www.stellar.org) network.

```
$./whisper.py -h
whisper.

Usage:
  whisper.py (-r [-n N] | -s MSG -a ADDR) [-k FILE]
  whisper.py -h | --help
  whisper.py -v | --version

Options:
  -r            Read messages.
  -s MSG        The message text to send.
  -a ADDR       The destination address (required for sending).
  -n N          Read last N messages (optional for reading) [default: 1].
  -k FILE       Path to the file containing the password-protected stellar
                seed for your account [default: ~/.stellar/wallet].
  -v --version  Display version and exit.
  -h --help     Show this screen.
```

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
- **Plausible deniability (optional):** some protocols contain optional fields for hashes which are indistinguishable from encrypted messages and the sender himself cannot decode the sent messages if ephemeral key pairs were used.

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

Bob calculates the shared secret by using his secret key and Alice's public key using the `ECDH` algorithm. Alice does the same calculation using her secret key and Bob's public key.  Let's call this shared 256-bit secret value `k`,

```
k = ECDH(pk_Alice, sk_Bob) = ECDH(pk_Bob, sk_Alice)
```

#### Step 2: Message encapsulation

The encapsulation is easiest to describe on an example. Imagine wanting to transmit a 46 byte long payload. The payload itself is a suitably *encoded* plaintext message or a small file that Bob wants to transmit.

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

  | Length (L) | Header 1-5      | Description                                                |
  | ---------- | --------------- | ---------------------------------------------------------- |
  | 1 ... 31   | 00001 ... 11111 | Last fragment of the payload of size L                     |
  | 0          | 00000           | Full-size fragment, payload continues in the next fragment |

  The next 3 bits of the header encode the encoding:

  | Header 6-8 | Content | Description | Symbol rate                                    |
  | ----------- | ------------------------- | ------------------------------------------------------------ | -------------------------- |
  | 000 | binary                    | no encoding, raw 8-bit                                       | 31 B / fragment      |
  | 001         | SMS TEXT                  | [GSM 03.38 charset](https://www.openmarket.com/docs/Content/Images/sms/characterset-gsm-characters.png) | 35 characters / fragment |
  | 010         | restricted uppercase TEXT | [Sixbit ASCII](http://catb.org/gpsd/AIVDM.html#_ais_payload_data_types) | 41 characters / fragment |
  | 011         | TEXT                      | [smaz](https://github.com/antirez/smaz)/[smac](https://github.com/servalproject/smac/blob/master/README) compression | ~ 31 - 60 B / fragment |
  | 100         | RESERVED for future use |||
  | 101         | RESERVED for future use |||
  | 110         | RESERVED for future use |||
  | 111         | RESERVED for future use |||

  For example, the headers of fragments the above hypothetical 46 B compression-encoded payload would like this:

      |0 1 2 3 4 5 6 7|
      ┌─┬─┬─┬─┬─┬─┬─┬─┐
      |0 0 0 0 0|0 1 1|    header of Fragment 1
      └─┴─┴─┴─┴─┴─┴─┴─┘
      ┌─┬─┬─┬─┬─┬─┬─┬─┐
      |0 1 1 1 1|0 1 1|    header of Fragment 2
      └─┴─┴─┴─┴─┴─┴─┴─┘

The combination of the header and the fragment will be called a block.

#### Step 3: Encryption

- Let's call `b_i` a (zero-padded, if required) block of the payload.

- The initiation vector (nonce) is given by the binary sum of the first 16 bytes of Alice's public key,

        IV = (pk_Alice[0:16] + sequence_number)[-16:]

    Here `sequence_number` is the sequential and increasing number attached to the transaction and incremented in Bob's account after the transaction has been settled. This construction assures that `IV` is unique and direction-dependent. If Alice send Bob a message, the `IV` will be given by the sum of *Bob's* public key and the `sequence_number` of *Alice's* acount. Never reusing the same `IV` is critically important. Failing to do so would catastrophically compromise the encryption (remember both Alice and Bob share the same secret `k`). With the proposed `IV` construction, even if Alice sends Bob the exact same plaintext message within a transaction with the exact same `sequence_number` (the sequence number is only guaranteed to be unique for each Stellar account separately), the `IV` is guaranteed to be different.

    The encrypted block will then be

        c_i = AES(b_i, IV, k)

    With the construction of the `IV` we have essentially selected the [CTR](https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation#Counter_(CTR)) mode of operation for AES.

- *Optional:* It is also possible to chain multiple encryptions (even though I don't think that is necessary, AES should provide plenty of security margin). In this case we need to extend the 256-bit shared secret to more, e.g. 512, bits using a suitable Key Derivation Function

        k1 || k2 = KDF(k)

    The first encryption round (using AES-256) is then

        c_i' = AES(b_i, IV, k1)

    and the second encryption round (for example, using Twofish)

        c_i = Twofish(c_i', IV, k2)

#### Step 4: Sending the message

The encrypted blocks `c_i` are set to the 32 byte `MEMO_HASH` field of the Stellar transaction object. A payment transaction is constructed (e.g. using the 0.0000001 XLM minimum amount). The total cost in this case will be 0.00000101 XLM per fragment (the total cost is the sum of the transaction fee and the payment amount). The transactions for all message fragments are executed sequentially with consecutive sequence numbers.

#### Step 5: Decryption, Assembly, Extraction and Decoding

Basically, for receiving the message, the corresponding inverse operations of steps 1-4 are performed at the receiving site in the opposite order: the encrypted blocks are decrypted and assembled into the payload (removing the headers and padding), and finally the payload is decoded.

## Proof of concept

The application is running on TESTNET at the moment, but that can easily be switched as soon as the security measures for protecting your seed are implemented (see TODO).

Bob can send a message to Alice (identified by this address [GCU2R...7ZDH](http://testnet.stellarchain.io/address/GCU2RRJHYBEIP6R6SJHLTCC32FVFGATYMTYB3ZBKT3OMPZLCTVSS7ZDH)):

```
$./whisper.py -s "Wow! A message through Stellar!" -a GCU2RRJHYBEIP6R6SJHLTCC32FVFGATYMTYB3ZBKT3OMPZLCTVSS7ZDH -k .bob_wallet
Enter password:
Sending message to GCU2RRJHYBEIP6R6SJHLTCC32FVFGATYMTYB3ZBKT3OMPZLCTVSS7ZDH...
Done.
```

Alice can indeed read the message.

```
$./whisper.py -r -n 1 -k .alice_wallet
Enter password:
Last 1 message(s)...
  1) Wow! A message through Stellar!
```

## TODO

- [x] Implement password protection for the seed file.
- [ ] Implement the defined message encodings.
- [ ] Introduce argument for specifying the cursor from where to start reading messages.
- [ ] Integrate federation address handling.
- [ ] Make the implementation cleaner (refactor).
- [ ] Provide a library, e.g. for integrating into wallet software.
