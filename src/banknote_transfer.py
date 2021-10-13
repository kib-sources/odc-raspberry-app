import json
import time
from typing import List

import core.crypto as crypto
from PiService import PiService
from core.Banknote import Banknote
from core.BanknoteWithBlockchain import BanknoteWithBlockchain
from core.Block import Block
from core.Wallet import Wallet


def transfer_banknotes(service: PiService, wallet: Wallet, banknotes: List[BanknoteWithBlockchain]):
    amount = sum(it.banknote.amount for it in banknotes)
    service.send_to_client(data={"amount": amount})

    for banknote in banknotes:
        transfer_banknote(service=service, wallet=wallet, banknote_with_blockchain=banknote)


def transfer_banknote(service: PiService, wallet: Wallet, banknote_with_blockchain: BanknoteWithBlockchain):
    otok, otpk = crypto.init_pair()

    service.send_to_client(data={"amount": banknote_with_blockchain.banknote.amount})

    # Шаги 1-2
    protected_block = {
        "parentSok": wallet.sok,
        "parentSokSignature": wallet.sok_signature,
        "parentOtokSignature": banknote_with_blockchain.blocks[0].otok,
        "time": round(time.time()),

        "otokSignature": "",
        "transactionSignature": "",
        "refUuid": None,
        "sok": None,
        "sokSignature": None
    }
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

    # Шаг 3 (на клиенте)

    # Шаг 4
    buff = service.receive_from_client()
    print(buff)
    acceptance_blocks = json.loads(buff)
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
    service.send_to_client(data={"childFull": block})
