import json
import logging
import time

import core.crypto as crypto
from PiService import PiService
from Wallet import Wallet
from core.Banknote import Banknote
from core.BanknoteWithBlockchain import BanknoteWithBlockchain
from core.Block import Block
from core.banknotes_distribution import select_banknotes_from_bag


def transfer_banknotes(service: PiService, wallet: Wallet, pulse_count: int):
    banknote_map = {2: 50, 3: 100, 4: 500, 5: 1000, 6: 5000, 7: 200, 8: 2000}
    amount = banknote_map[pulse_count]
    print(f"bucks inserted: {amount}")

    try:
        select_banknotes_from_bag(wallet.banknotes, amount)
    except AssertionError:
        wallet.refill(amount)

    sublist_indexes = select_banknotes_from_bag(wallet.banknotes, amount)
    for i in sublist_indexes:
        _transfer_banknote(service=service, wallet=wallet, banknote_with_blockchain=wallet.banknotes[i])

    for i in sublist_indexes:
        del wallet.banknotes[i]


def _transfer_banknote(service: PiService, wallet: Wallet, banknote_with_blockchain: BanknoteWithBlockchain):
    print("sending", banknote_with_blockchain.banknote.amount, "bucks")

    otok, otpk = crypto.init_pair()

    # Шаг 0
    service.send_to_client(data={"amount": banknote_with_blockchain.banknote.amount})

    # Шаг 1
    protected_block = {
        "parentSok": wallet.sok,
        "parentSokSignature": wallet.sok_signature,
        "parentOtokSignature": banknote_with_blockchain.blocks[0].otok_signature,
        "time": round(time.time()),

        "otokSignature": "",
        "transactionSignature": "",
        "refUuid": None,
        "sok": None,
        "sokSignature": None
    }

    # Шаг 2
    payload = {
        "banknoteWithBlockchain": {
            "banknoteWithProtectedBlock": {
                "banknote": Banknote.to_dict(banknote_with_blockchain.banknote),
                "protectedBlock": protected_block
            },
            "blocks": [Block.to_dict(it) for it in banknote_with_blockchain.blocks],
        }
    }
    service.send_to_client(data=payload)
    print("protected block transfered")

    # Шаг 3 (на клиенте)

    # Шаг 4
    buff = service.receive_from_client()
    acceptance_blocks = json.loads(buff)["blocks"]
    block = Block.from_dict(acceptance_blocks["childBlock"])

    # Шаг 5
    magic, subscribe_transaction_hash, subscribe_transaction_signature = wallet.subscribe(
        block.uuid,
        block.parent_uuid,
        block.bnid
    )

    block.magic = magic
    block.subscribe_transaction_hash = subscribe_transaction_hash
    block.subscribe_transaction_signature = subscribe_transaction_signature

    # Шаг 6
    payload = {
        "childFull": block.to_dict()
    }
    service.send_to_client(data=payload)
    print("banknote transfered")
