import json
from typing import Optional, Dict

import requests
import logging
import copy

from src.block import Block
from src.wallet import Wallet
from src.transaction import Transaction
from src.utils.hash_util import hash_block
from src.utils.verification import Verification

# The reward we give to miners for creating a new block
MINING_REWARD = 2


class Blockchain:
    """ The class manages the chain of blocks as well as open transactions and the node on which it's running.
    :argument public_key: The connected node (witch runs the blockchain).
    :argument node_id: The port witch runs the node.
    """

    def __init__(self, public_key, node_id):
        self.genesis_block = Block(index=0, previous_hash="", transactions=[], proof=77, timestamp=0)
        self.chain = [self.genesis_block]
        self.__open_transactions = []
        self.public_key = public_key
        self.__peer_nodes = set()
        self.node_id = node_id
        self.is_resolve_conflicts = False
        self.load_data()

    @property
    def chain(self):
        return copy.deepcopy(self.__chain)

    @chain.setter
    def chain(self, val):
        self.__chain = val

    def get_open_transactions(self) -> list:
        """ Returns a copy of open transactions list. """
        return copy.deepcopy(self.__open_transactions)

    def load_data(self) -> None:
        """ Downloads blockchain data, open transactions, and node list from a local file. """
        try:
            with open(f"blockchain-{self.node_id}.txt", mode="r") as file:
                file_content = file.readlines()
                # Loading blockchain
                blockchain = json.loads(file_content[0][:-1])
                self.chain = [
                    Block(
                        index=block["index"],
                        previous_hash=block["previous_hash"],
                        transactions=[
                            Transaction(
                                sender=tx["sender"],
                                recipient=tx["recipient"],
                                signature=tx["signature"],
                                amount=tx["amount"]
                            ) for tx in block["transactions"]
                        ],
                        proof=block["proof"],
                        timestamp=block["timestamp"]) for block in blockchain
                ]
                # Loading open transactions
                open_transactions = json.loads(file_content[1][:-1])
                self.__open_transactions = [
                    Transaction(
                        sender=tx["sender"],
                        recipient=tx["recipient"],
                        signature=tx["signature"],
                        amount=tx["amount"]
                    ) for tx in open_transactions
                ]
                # Loading node list
                self.__peer_nodes = set(json.loads(file_content[2]))
        except (IOError, IndexError) as ex:
            logging.error(f"Error loading data: {ex}")

    def save_data(self) -> None:
        """ Saves the current blockchain, open transactions and node list to a file. """
        try:
            serialized_chain = [
                {
                    "index": block.index,
                    "previous_hash": block.previous_hash,
                    "transactions": [tx.__dict__ for tx in block.transactions],
                    "proof": block.proof,
                    "timestamp": block.timestamp
                } for block in self.chain
            ]
            serialized_tx = [tx.__dict__ for tx in self.__open_transactions]
            peer_nodes_list = list(self.__peer_nodes)
            with open(f"blockchain-{self.node_id}.txt", mode="w") as file:
                file.write("\n".join([
                    json.dumps(serialized_chain, ensure_ascii=False),
                    json.dumps(serialized_tx, ensure_ascii=False),
                    json.dumps(peer_nodes_list, ensure_ascii=False)
                ]))
        except IOError as ex:
            logging.error(f"Error saving data: {ex}")

    def proof_of_work(self) -> int:
        """ Performs the Proof of Work mechanism by finding a proof value
        that makes the hash meet the difficulty requirements.
        :return: The value found proof.
        """
        last_block = self.__chain[-1]
        last_hash = hash_block(block=last_block)
        proof = 0
        while not Verification.valid_of_proof(
                transactions=self.__open_transactions,
                last_hash=last_hash,
                proof=proof):
            proof += 1
        return proof

    def get_balance(self, sender: str = None) -> float | None:
        """ Calculates the balance of a blockchain participant.
        :argument sender: The user's address (if None, public_key is used).
        :return: The user's current balance (int or None if no key).
        """
        if sender is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = sender
        # All sent transactions (in blocks + open)
        amount_sent = sum(
            tx.amount for block in self.__chain for tx in block.transactions if tx.sender == participant
        ) + sum(
            tx.amount for tx in self.__open_transactions if tx.sender == participant
        )
        # All received transactions (in blocks only)
        amount_received = sum(
            tx.amount for block in self.__chain for tx in block.transactions if tx.recipient == participant
        )
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns the last item of the current blockchain. """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

    def add_transaction(self, recipient: str, sender: str, signature: str, amount=1.0,
                        is_receiving: bool = False) -> bool:
        """ Append a new transaction to the list of open transactions.
        :argument recipient: The recipient of the transaction.
        :argument sender: The sender of the transaction.
        :argument signature: The digital signature of the transaction.
        :argument amount: The amount to transfer (default 1.0).
        :argument is_receiving: A flag to prevent resending when receiving the transaction.
        :return: True if the transaction was added successfully, otherwise False.
        """
        transaction = Transaction(sender=sender, recipient=recipient, signature=signature, amount=amount)
        if not Verification.verify_transaction(transaction=transaction, get_balance=self.get_balance):
            return False
        self.__open_transactions.append(transaction)
        self.save_data()
        if not is_receiving:
            for node in self.__peer_nodes:
                url = f"http://{node}:5000/broadcast-transaction"
                try:
                    response = requests.post(url=url, json={
                        "sender": sender,
                        "recipient": recipient,
                        "signature": signature,
                        "amount": amount
                    })
                    if response.status_code >= 400:
                        logging.warning(f"Transaction rejected by node {node}, conflict resolution required.")
                        return False
                except requests.exceptions.ConnectionError:
                    logging.error(f"Failed to connect to node {node}. Skipping it.")
                    continue
        return True

    def mine_block(self) -> Optional[Block]:
        """ Creates a new block, mines it (Proof of Work) and broadcasts it over the network.
        :return: The created block if mining was successful, otherwise None.
        """
        if self.public_key is None:
            logging.warning("Miner public key missing.")
            return None
        last_block = self.__chain[-1]
        hashed_block = hash_block(block=last_block)
        proof = self.proof_of_work()
        # Create a reward transaction for mining
        reward_transaction = Transaction(
            sender="MINING",
            recipient=self.public_key,
            signature="",
            amount=MINING_REWARD)
        # Copy open transactions to avoid changes during operation
        copied_transactions = copy.deepcopy(self.__open_transactions)
        # Check the correctness of all transactions
        if not all(Wallet.verify_transaction(tx) for tx in copied_transactions):
            logging.warning("Open transactions have not been verified.")
            return None
        # Adding a reward transaction
        copied_transactions.append(reward_transaction)
        # Create and add a new block
        block = Block(
            index=len(self.__chain),
            previous_hash=hashed_block,
            transactions=copied_transactions,
            proof=proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        # Sending a block over the network
        for node in self.__peer_nodes:
            url = f"http://{node}:5000/broadcast-block"
            converted_block = block.__dict__.copy()
            converted_block["transactions"] = [tx.__dict__ for tx in converted_block["transactions"]]
            try:
                response = requests.post(url=url, json={
                    "block": converted_block
                })
                if response.status_code >= 400:
                    logging.warning(f"Block declined by node {node}, conflict resolution required.")
                if response.status_code == 409:
                    self.is_resolve_conflicts = True
                    logging.info("Chain conflict detected, resolution started")
            except requests.exceptions.ConnectionError:
                logging.error(f"Failed to connect to node {node}. Skipping it.")
                continue
        return block

    def add_block(self, block: Dict) -> bool:
        """ Adds a block to the chain if it passes validation.
        :argument block: A dictionary containing the block data.
        :return: True if the block was successfully added, otherwise False.
        """
        transactions = [Transaction(
            sender=tx["sender"],
            recipient=tx["recipient"],
            signature=tx["signature"],
            amount=tx["amount"]) for tx in block["transactions"]]
        proof_is_valid = Verification.valid_of_proof(
            transactions=transactions[:-1],
            last_hash=block["previous_hash"],
            proof=block["proof"])
        hashes_match = hash_block(self.chain[-1]) == block["previous_hash"]
        if not proof_is_valid or not hashes_match:
            logging.warning("The block didn't pass the check. Decline.")
            return False
        self.__chain.append(Block(
            index=block["index"],
            previous_hash=block["previous_hash"],
            transactions=transactions,
            proof=block["proof"],
            timestamp=block["timestamp"]))
        # If there are any open transactions that are already included in the block, we delete them
        if self.__open_transactions:
            stored_transactions = copy.deepcopy(self.__open_transactions)
            for itx in block["transactions"]:
                for open_tx in stored_transactions:
                    if (open_tx.sender == itx["sender"] and
                            open_tx.recipient == itx["recipient"] and
                            open_tx.signature == itx["signature"] and
                            open_tx.amount == itx["amount"]):
                        if open_tx in self.__open_transactions:
                            self.__open_transactions.remove(open_tx)
        self.save_data()
        logging.info("The block has been successfully added to the chain.")
        return True

    def resolve_conflicts(self) -> bool:
        """ Resolves conflicts in the blockchain by choosing the longest valid chain.
        :return: True if the local chain has been replaced, otherwise False.
        """
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = f"http://{node}:5000/chain"
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                node_chain_data = response.json()
                if not isinstance(node_chain_data, list):
                    logging.warning(f"Invalid chain received from {node}. Skipping it.")
                    continue
                node_chain_length = len(node_chain_data)
                local_chain_length = len(self.chain)
                if node_chain_length <= local_chain_length:
                    continue  # Discard the chain if it is shorter
                node_chain = [
                    Block(
                        index=block["index"],
                        previous_hash=block["previous_hash"],
                        transactions=[
                            Transaction(
                                sender=tx["sender"],
                                recipient=tx["recipient"],
                                signature=tx["signature"],
                                amount=tx["amount"]
                            ) for tx in block["transactions"]
                        ],
                        proof=block["proof"],
                        timestamp=block["timestamp"]) for block in node_chain_data
                ]
                if Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.RequestException as e:
                logging.error(f"Error requesting {node}: {e}")
            except (KeyError, TypeError, ValueError) as e:
                logging.error(f"Error processing chain data from {node}: {e}")
        self.is_resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
            logging.info("The chain was replaced with a longer one..")
        else:
            logging.info("The local chain remains unchanged.")
        self.save_data()
        return replace

    def add_peer_node(self, node):
        """ Adds new node in the peer node set.
        :argument node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """ Removes a node from the peer node set.
        :argument node: The node URL which should be removed.
        """
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        """ Returns a list of all connected peer nodes. """
        return list(self.__peer_nodes)
