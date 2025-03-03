import logging

from src.utils.hash_util import hash_string_256, hash_block
from src.wallet import Wallet


class Verification:
    """ Provides verification helper methods. """

    @staticmethod
    def valid_of_proof(transactions: list, last_hash: str, proof: int) -> bool:
        """ Checks whether a proof is correct (four leading 0s).
        :argument transactions: List of transactions.
        :argument last_hash: Hash of the previous block.
        :argument proof: Numerical value of the proof.
        :return: True if the proof is correct, False otherwise.
        """
        guess_hash = hash_string_256(f"{[tx.to_ordered_dict for tx in transactions]}{last_hash}{proof}")
        logging.debug(guess_hash)
        return guess_hash[0:4] == "0000"

    @classmethod
    def verify_chain(cls, blockchain) -> bool:
        """ Checks the integrity of the blockchain by checking block hashes and proofs of work.
        :argument blockchain: List of blocks in the chain.
        :return: True if the blockchain is correct, otherwise False.
        """
        for (index, block) in enumerate(blockchain):
            if index == 0:
                # Genesis block
                continue
            if block.previous_hash != hash_block(block=blockchain[index - 1]):
                logging.error(f"Blockchain corrupted at block: {index}")
                return False
            if not cls.valid_of_proof(
                    transactions=block.transactions[:-1],
                    last_hash=block.previous_hash,
                    proof=block.proof):
                logging.error(f"Invalid Proof of Work at block: {index}")
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_funds=True) -> bool:
        """ Checks the correctness of the transaction.
        :argument transaction: Transaction object.
        :argument get_balance: Function to get the sender's balance.
        :argument check_funds: Flag indicating whether the sender's balance should be checked.
        :return: True if the transaction is valid, otherwise False.
        """
        if check_funds:
            # Check sender's balance
            sender_balance = get_balance(sender=transaction.sender)
            if sender_balance < transaction.amount:
                logging.warning("The sender doesn't have sufficient funds.")
                return False
        # Verify transaction
        return Wallet.verify_transaction(transaction=transaction)

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance) -> bool:
        """ Check all open transactions.
        :argument open_transactions: List of open transactions.
        :argument get_balance: Function to get the sender's balance.
        :return: True if all transactions are valid, otherwise False.
        """
        return all([cls.verify_transaction(
            transaction=tx,
            get_balance=get_balance,
            check_funds=False) for tx in open_transactions])
