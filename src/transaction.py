from collections import OrderedDict

from src.utils.printable import Printable


class Transaction(Printable):
    """ A transaction witch can be added to a block in the blockchain.
    :argument sender: The sender of the coins.
    :argument recipient: The recipient of the coins.
    :argument signature: The signature of the transaction.
    :argument amount: The amount of coins sent.
    """

    def __init__(self, sender, recipient, signature, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.signature = signature

    def to_ordered_dict(self):
        """ Return ordered dictionary for fields of transaction. """
        return OrderedDict([
            ("sender", self.sender),
            ("recipient", self.recipient),
            ("amount", self.amount)
        ])
