from typing import Optional, List

from core.BanknoteChain import BanknoteChain
from core.crypto import init_pair
from server_api import register_wallet, issue_and_receive_banknotes


class Wallet:
    sok: str
    spk: str
    wid: str
    banknotes: List[BanknoteChain]

    # TODO
    sok_signature: str
    bok: str

    def __init__(self):
        self.sok, self.spk = init_pair()
        self.wid = register_wallet(self.sok)
        self.banknotes = list()

    def refill(self, amount: int):
        banknotes: Optional[list] = issue_and_receive_banknotes(amount, self.wid, self.spk)
        self.banknotes += banknotes

    def deposit_size(self):
        return sum(it.banknote.amount for it in self.banknotes)


# Example
if __name__ == "__main__":
    wallet = Wallet()
    wallet.refill(300)
    wallet.refill(25)

    print("$", wallet.deposit_size())
    print(len(wallet.banknotes), "банкнот")
