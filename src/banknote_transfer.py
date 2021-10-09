import json
from typing import List

import core.crypto as crypto
from AtmService import AtmService
from core.BanknoteWithBlockchain import BanknoteWithBlockchain
from core.Block import Block
from core.Wallet import Wallet


def transfer_banknotes(service: AtmService, wallet: Wallet, banknotes: List[BanknoteWithBlockchain]):
    amount = sum(it.banknote.amount for it in banknotes)
    service.send_to_client(data={"amount": amount})

    for banknote in banknotes:
        transfer_banknote(service=service, wallet=wallet, banknote=banknote)


def transfer_banknote(service: AtmService, wallet: Wallet, banknote: BanknoteWithBlockchain):
    otok, otpk = crypto.init_pair()

    service.send_to_client(data={"amount": banknote.banknote.amount})

    # Шаги 1-2
    protected_block = {
        "parentSok": wallet.sok,
        "parentSokSignature": wallet.sok_signature,
        "parentOtokSignature": banknote.blockchain[0].otok
    }
    banknote.blockchain += protected_block
    service.send_to_client(data={"blockchain": BanknoteWithBlockchain.to_dict(banknote)})

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
