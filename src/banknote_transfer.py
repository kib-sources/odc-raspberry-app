import logging
import time
import cbor2 as cbor

from Wallet import Wallet
from core.Banknote import Banknote
from core.BanknoteWithBlockchain import BanknoteWithBlockchain
from core.Block import Block
from core.banknotes_distribution import select_banknotes_from_bag


def transfer_banknotes(service, wallet: Wallet, amount: int):
    """Передает указанную сумму текущему клиенту

    :param amount: сумма для отправки
    :param wallet: объект класса Wallet
    :param service: объект класса PiService или NfcService
    """

    logging.info(f"banknote inserted: {amount}")

    try:
        select_banknotes_from_bag(wallet.banknotes, amount)
    except AssertionError:
        wallet.refill(max([amount, 2000]))

    sublist_indexes = select_banknotes_from_bag(wallet.banknotes, amount)

    service.send_to_client(data={"amount": amount})

    for i in sublist_indexes:
        _transfer_banknote(service=service, wallet=wallet, banknote_with_blockchain=wallet.banknotes[i])

    for i in sublist_indexes[::-1]:
        del wallet.banknotes[i]


def _transfer_banknote(service, wallet: Wallet, banknote_with_blockchain: BanknoteWithBlockchain):
    """Передает указанную банкноту текущему клиенту

    :param service: количество цифровых сигналов, пришедших на пин от купюроприемника
    :param wallet: объект класса Wallet
    """

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

    # Шаг 3 (на клиенте)

    # Шаг 4
    buff = service.receive_from_client()
    acceptance_blocks = cbor.loads(buff)["blocks"]
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

    print("Sent: " + str(banknote_with_blockchain.banknote.amount))
