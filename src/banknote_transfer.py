import json
from typing import List, Union

from AtmService import AtmService
from BluetoothServiceStunt import BluetoothServiceStunt
from core.BanknoteWithBlockchain import BanknoteWithBlockchain
from core.Block import Block
from core.Wallet import Wallet
import core.crypto as crypto

IBluetoothService = Union[AtmService, BluetoothServiceStunt]


def transfer_banknotes(service: AtmService, wallet: Wallet, banknotes: List[BanknoteWithBlockchain]):
    amount = sum(it.banknote.amount for it in banknotes)
    service.send_to_client(data={"amount": amount})

    for banknote in banknotes:
        transfer_banknote(service=service, wallet=wallet, banknote=banknote)


def transfer_banknote(service: IBluetoothService, wallet: Wallet, banknote: BanknoteWithBlockchain):
    otok, otpk = crypto.init_pair()

    # Шаг 1
    protected_block = {
        "parentSok": wallet.sok,
        "parentSokSignature": wallet.sok_signature,
        "parentOtokSignature": banknote.blockchain[0].otok
    }
    banknote.blockchain += protected_block
    payload_container = {
        "blockchain": banknote
    }

    # Шаг 2
    service.send_to_client(data=payload_container)

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
    payload_container = {
        "childFull": block
    }
    service.send_to_client(data=payload_container)
