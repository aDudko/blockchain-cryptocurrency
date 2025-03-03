import hashlib as hl
import json

import src.block


def hash_string_256(string: str) -> str:
    """ Calculates the SHA-256 hash for the given string.
    :argument string: The string which should be hashed.
    :return: SHA-256 hash as a hexadecimal string.
    """
    return hl.sha256(string.encode("utf-8")).hexdigest()


def hash_block(block: src.block.Block) -> str:
    """ Calculates the SHA-256 hash for the given block.
    :argument block: The block that should be hashed.
    :return: SHA-256 hash of the block as a hexadecimal string.
    """
    hashable_block = block.__dict__.copy()
    hashable_block["transactions"] = [tx.to_ordered_dict() for tx in hashable_block["transactions"]]
    return hash_string_256(json.dumps(hashable_block, sort_keys=True))
