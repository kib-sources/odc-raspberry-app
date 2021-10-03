from typing import Optional, List, Union
from uuid import UUID

from core.BanknoteWithBlockchain import BanknoteWithBlockchain
import core.crypto as crypto
from server_api import register_wallet, issue_and_receive_banknotes


class Wallet:
    sok: str
    spk: str
    wid: str
    banknotes: List[BanknoteWithBlockchain]

    # TODO
    sok_signature: str
    bok: str

    def __init__(self):
        self.sok, self.spk = crypto.init_pair()
        self.wid = register_wallet(self.sok)
        self.banknotes = list()

    def refill(self, amount: int):
        banknotes: Optional[list] = issue_and_receive_banknotes(amount, self.wid, self.spk)
        self.banknotes += banknotes

    def deposit_size(self):
        return sum(it.banknote.amount for it in self.banknotes)

    def subscribe(self, uuid: Union[UUID, str], parent_uuid: Union[UUID, str], bnid):
        parent_uuid = str(parent_uuid)
        uuid = str(uuid)
        if parent_uuid not in self._bag:
            raise Exception(f"Уже передан блок с uuid={parent_uuid} или данного блока никогда не было в кошельке")

        otpk = self._bag[parent_uuid]

        magic = crypto.random_magic()

        _subscribe_transaction_hash = crypto.subscribe_transaction_hash(uuid, magic, bnid)
        _subscribe_transaction_signature = crypto.signature(_subscribe_transaction_hash, otpk)

        # Удаляем ключ, чтобы более ни разу нельзя было подписывать
        #   в нормальном решении необходимо хранение на доверенном носителе, например на SIM
        del self._bag[parent_uuid]

        return magic, _subscribe_transaction_hash, _subscribe_transaction_signature


# Example
if __name__ == "__main__":
    wallet = Wallet()
    wallet.refill(300)
    wallet.refill(25)

    print("$", wallet.deposit_size())
    print(len(wallet.banknotes), "банкнот")
