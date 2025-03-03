from http import HTTPStatus
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from src.blockchain import Blockchain
from src.wallet import Wallet

app = Flask(__name__, static_folder="static")
CORS(app=app)


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)


### Blocks and Blockchain ###

@app.route("/mine", methods=["POST"])
def mine():
    if blockchain.is_resolve_conflicts:
        response = {
            "message": "Resolve conflicts first, block not added.",
        }
        return jsonify(response), HTTPStatus.CONFLICT
    block = blockchain.mine_block()
    if block is not None:
        dict_block = block.__dict__.copy()
        dict_block["transactions"] = [tx.__dict__ for tx in dict_block["transactions"]]
        response = {
            "message": "Block added successfully",
            "block": dict_block,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), HTTPStatus.OK
    else:
        response = {
            "message": "Adding new block failed.",
            "wallet_set_up": wallet.public_key is not None
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/resolve-conflicts", methods=["POST"])
def resolve_conflicts():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            "message": "Chain was replaced.",
            "chain": [block.__dict__ for block in blockchain.chain]
        }
    else:
        response = {
            "message": "Local chain was winner."
        }
    return jsonify(response), HTTPStatus.OK


@app.route("/chain", methods=["GET"])
def get_chain():
    dict_chain = [block.__dict__.copy() for block in blockchain.chain]
    for dict_block in dict_chain:
        dict_block["transactions"] = [tx.__dict__ for tx in dict_block["transactions"]]
    return jsonify(dict_chain), HTTPStatus.OK


### Transactions ###

@app.route("/broadcast-transaction", methods=["POST"])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {
            "message": "No data found."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    required = ["sender", "recipient", "signature", "amount"]
    if not all(key in values for key in required):
        response = {
            "message": "Some data is missing."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    success = blockchain.add_transaction(
        sender=values["sender"],
        recipient=values["recipient"],
        signature=values["signature"],
        amount=values["amount"],
        is_receiving=True)
    if success:
        response = {
            "message": "Successfully added transaction.",
            "transaction": {
                "sender": values["sender"],
                "recipient": values["recipient"],
                "signature": values["signature"],
                "amount": values["amount"]
            }
        }
        return jsonify(response), HTTPStatus.CREATED
    else:
        response = {
            "message": "Creating a transaction failed."
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/broadcast-block", methods=["POST"])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {
            "message": "No data found."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    if "block" not in values:
        response = {
            "message": "Block is missing."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    block = values["block"]
    if block["index"] == blockchain.chain[-1].index + 1:
        if blockchain.add_block(block=block):
            response = {
                "message": "Block added."
            }
            return jsonify(response), HTTPStatus.CREATED
        else:
            response = {
                "message": "Block seems invalid."
            }
        return jsonify(response), HTTPStatus.CONFLICT
    elif block["index"] > blockchain.chain[-1].index:
        response = {
            "message": "Blockchain seems to differ from to local blockchain."
        }
        blockchain.is_resolve_conflicts = True
        return jsonify(response), HTTPStatus.OK
    else:
        response = {
            "message": "Blockchain seems to be shorter, block not added."
        }
        return jsonify(response), HTTPStatus.CONFLICT


@app.route("/transaction", methods=["POST"])
def add_transaction():
    if wallet.public_key is None:
        response = {
            "message": "No wallet set up."
        }
        return jsonify(response), HTTPStatus.NOT_ACCEPTABLE
    values = request.get_json()
    if not values:
        response = {
            "message": "No data found."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    required_fields = ["recipient", "amount"]
    if not all(field in values for field in required_fields):
        response = {
            "message": "Required data is missing."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    recipient = values["recipient"]
    amount = values["amount"]
    if amount <= 0:
        response = {
            "message": "Amount must be positive."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    signature = wallet.sign_transaction(sender=wallet.public_key, recipient=recipient, amount=amount)
    success = blockchain.add_transaction(
        sender=wallet.public_key,
        recipient=recipient,
        signature=signature,
        amount=amount)
    if success:
        response = {
            "message": "Successfully added transaction.",
            "transaction": {
                "sender": wallet.public_key,
                "recipient": recipient,
                "signature": signature,
                "amount": amount
            },
            "funds": blockchain.get_balance()
        }
        return jsonify(response), HTTPStatus.CREATED
    else:
        response = {
            "message": "Creating a transaction failed."
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), HTTPStatus.OK


### Wallet ###

@app.route("/wallet", methods=["POST"])
def create_wallet():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(public_key=wallet.public_key, node_id=port)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), HTTPStatus.CREATED
    else:
        response = {
            "message": "Saving keys failed."
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/wallet", methods=["GET"])
def load_wallet():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(public_key=wallet.public_key, node_id=port)
        response = {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "funds": blockchain.get_balance()
        }
        return jsonify(response), HTTPStatus.OK
    else:
        response = {
            "message": "Loading keys failed."
        }
        return jsonify(response), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route("/balance", methods=["GET"])
def get_balance():
    balance = blockchain.get_balance()
    if wallet.public_key is None:
        response = {
            "message": "No wallet set up. Please create a wallet first."
        }
        return jsonify(response), HTTPStatus.NOT_ACCEPTABLE
    if balance is not None:
        response = {
            "message": "Fetched balance successfully.",
            "funds": balance
        }
        return jsonify(response), HTTPStatus.OK


### Nodes ###

@app.route("/node", methods=["POST"])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            "message": "No data attached."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    if "node" not in values:
        response = {
            "message": "No node data found."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    node = values["node"]
    blockchain.add_peer_node(node=node)
    response = {
        "message": "Node added successfully.",
        "all_nodes": blockchain.get_peer_nodes()
    }
    return jsonify(response), HTTPStatus.CREATED


@app.route("/node/<node_url>", methods=["DELETE"])
def remove_node(node_url):
    if node_url == "" or node_url is None:
        response = {
            "message": "No node found."
        }
        return jsonify(response), HTTPStatus.BAD_REQUEST
    blockchain.remove_peer_node(node=node_url)
    response = {
        "message": "Node removed successfully.",
        "all_nodes": blockchain.get_peer_nodes()
    }
    return jsonify(response), HTTPStatus.OK


@app.route("/node", methods=["GET"])
def get_nodes():
    response = {
        "all_nodes": blockchain.get_peer_nodes()
    }
    return jsonify(response), HTTPStatus.OK


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=5000)
    args = parser.parse_args()
    port = args.port
    wallet = Wallet(node_id=port)
    blockchain = Blockchain(public_key=wallet.public_key, node_id=port)
    app.run(host="0.0.0.0", port=port, debug=True)
