from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair

from docchain.config import config

import logging

__bdb = BigchainDB(config["BIGCHAIN"]["url"])


def gen_keypair():
    return generate_keypair()

def create_doc_for_sign(creator_pubkey,
    creator_privkey,
    signer_pubkey,
    document):
    prepared_create_tx = __bdb.transactions.prepare(
        operation='CREATE',
        signers=creator_pubkey,
        recipients=signer_pubkey,
        asset=document)

    fullfiled_create_tx = __bdb.transactions.fulfill(
        prepared_create_tx,
        private_keys=creator_privkey)

    commited_create_tx = __bdb.transactions.send_commit(fullfiled_create_tx)

    logging.info("Commited create tx:", commited_create_tx['id'])

def sign_document(tx_id, creator_pubkey, signer_privkey):

    metadata = {'signed': True}
    tx = __bdb.transactions.retrieve(tx_id)
    transfer_asset = {
        "id": tx_id
    }

    output_index = 0
    output = tx['outputs'][output_index]

    transfer_input = {
        'fulfillment': output['condition']['details'],
        'fulfills': {
            'output_index': output_index,
            'transaction_id': tx_id,
        },
        'owners_before': output['public_keys']
    }

    prepared_transfer_tx = __bdb.transactions.prepare(
        operation='TRANSFER',
        asset=transfer_asset,
        inputs=transfer_input,
        recipients=creator_pubkey,
        metadata=metadata)

    fulfilled_transfer_tx = __bdb.transactions.fulfill(
        prepared_transfer_tx,
        private_keys=signer_privkey)


    commited_transfer_tx = __bdb.transactions.send_commit(fulfilled_transfer_tx)

    logging.info("Commited transfer tx:", commited_transfer_tx['id'])
