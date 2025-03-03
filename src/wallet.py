import binascii
import logging

from Cryptodome import Random
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5


class Wallet:
    """ Manages private and public keys. Manages transaction signing and verification.
    :argument node_id: The port witch runs the node.
    """

    def __init__(self, node_id):
        self.private_key = None
        self.public_key = None
        self.node_id = node_id

    def create_keys(self) -> None:
        """ Create a new pair of public and private keys. """
        self.private_key, self.public_key = Wallet.generate_keys()
        logging.info("New keys have been created and saved.")

    def save_keys(self) -> bool:
        """ Saves RSA keys to local file.
        :return: `True` if saving is successful, `False` otherwise """
        if not self.public_key or not self.private_key:
            logging.error("Keys missing, saving impossible.")
            return False
        try:
            with open(f"wallet-{self.node_id}.txt", mode="w") as f:
                f.write(f"{self.public_key}\n{self.private_key}")
            return True
        except IOError as ex:
            logging.error(f"Error saving keys: {ex}")
            return False

    def load_keys(self) -> bool:
        """ Loads keys from local file
        :return: `True` if the keys were loaded successfully, otherwise `False`.
        """
        try:
            with open(f"wallet-{self.node_id}.txt", mode="r") as f:
                keys = [line.strip() for line in f.readlines()]
            if len(keys) < 2:
                logging.error("The key file is corrupted or empty.")
                return False
            self.public_key = keys[0]
            self.private_key = keys[1]
            return True
        except (IOError, IndexError) as ex:
            logging.error(f"Error loading keys: {ex}")
            return False

    @staticmethod
    def generate_keys() -> tuple[str, str]:
        """ Generates a pair of RSA keys (private and public) in HEX format.
        :return: Tuple of (private_key, public_key) as HEX strings.
        """
        try:
            # Generate RSA key
            private_key = RSA.generate(bits=3072, randfunc=Random.new().read)
            public_key = private_key.publickey()
            # Exporting keys in DER format (PKCS#8 for private)
            private_key_hex = binascii.hexlify(private_key.exportKey(format="DER", pkcs=8)).decode("ascii")
            public_key_hex = binascii.hexlify(public_key.exportKey(format="DER")).decode("ascii")
            return private_key_hex, public_key_hex
        except Exception as e:
            logging.error(f"Error generating keys: {e}")
            return "", ""

    def sign_transaction(self, sender: str, recipient: str, amount: float) -> str:
        """ Signs a transaction using a private key.
        :argument sender: The sender of the transaction.
        :argument recipient: The recipient of the transaction.
        :argument amount: The amount of the transaction.
        :return: The signature in HEX string format.
        """
        if not self.private_key:
            logging.error("Private key missing. Signature not possible.")
            return ""
        try:
            # Upload the private key and create a subscriber
            private_key = RSA.import_key(binascii.unhexlify(self.private_key))
            signer = PKCS1_v1_5.new(private_key)
            # Create a hash of the transaction data
            data = f"{sender}{recipient}{amount}".encode("utf-8")
            signature = signer.sign(SHA256.new(data))
            # Return the signature in hex format
            return binascii.hexlify(signature).decode("ascii")
        except (ValueError, TypeError, binascii.Error) as ex:
            logging.error(f"Error signing transaction: {ex}")
            return ""

    @staticmethod
    def verify_transaction(transaction) -> bool:
        """ Verifies the digital signature of a transaction using the RSA and SHA-256 algorithms.
        :argument transaction: The transaction to verify (must contain sender, recipient, amount, and signature).
        :return: `True` if the signature is valid, otherwise `False`.
        """
        if not all(hasattr(transaction, attr) and getattr(transaction, attr) for attr in
                   ["sender", "recipient", "amount", "signature"]):
            logging.error("Required fields are missing from the transaction.")
            return False
        try:
            # Decode the sender's public key
            public_key = RSA.import_key(binascii.unhexlify(transaction.sender))
            verifier = PKCS1_v1_5.new(public_key)
            # Create a transaction hash (without signature)
            data = f"{transaction.sender}{transaction.recipient}{transaction.amount}".encode("utf-8")
            h = SHA256.new(data)
            # Check signature
            return verifier.verify(h, binascii.unhexlify(transaction.signature))
        except (ValueError, TypeError, binascii.Error) as ex:
            logging.error(f"Signature verification error: {ex}")
            return False
