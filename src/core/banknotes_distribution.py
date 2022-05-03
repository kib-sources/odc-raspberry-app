from collections import Counter
from itertools import groupby
from operator import itemgetter
from typing import List

from core.BanknoteWithBlockchain import BanknoteWithBlockchain

# TODO не для всех сумм корректно подбираются банкноты
def select_banknotes_from_bag(bag: List[BanknoteWithBlockchain], amount: int):
    """Выбирает цифровые банкноты из хранилища для передачи клиенту
    :param bag : массив цифровых банкнот, хранимых в банкомате
    :param amount : сумма для передачи
    :return: банкноты для передачи
    """

    give_amounts = _split_banknotes_from_amount(amount)
    banknotes_in_wallet = [(it.banknote.amount, idx) for idx, it in enumerate(bag)]
    banknotes_in_wallet = sorted(banknotes_in_wallet, key=itemgetter(0))

    banknotes_to_give = list()
    for key, group in groupby(banknotes_in_wallet, itemgetter(0)):
        if key in give_amounts.keys():
            banknotes_to_give += list(group)[:give_amounts[key]]

    sum_ = sum(map(itemgetter(0), banknotes_to_give))
    print("transferring", sum_)
    assert sum_ == amount, f"Not enough banknotes! Only {sum_} remaining, but {amount} needed. {banknotes_to_give}"

    return list(map(itemgetter(1), banknotes_to_give))


def _split_banknotes_from_amount(amount: int):
    possible_amounts = [1, 2, 5, 10, 50, 100, 500, 1000, 2000, 5000]

    give_amounts = []
    for i in range(len(possible_amounts) - 1):
        give_amounts += [possible_amounts[i]] * (possible_amounts[i + 1] // possible_amounts[i] - 1)

    print(give_amounts)
    give_amounts += [2, 50, 50, 1000]
    give_amounts = sorted(give_amounts)

    for i in range(len(give_amounts)):
        bundle = give_amounts[:i + 1]
        if sum(bundle) >= amount:
            return dict(Counter(bundle))

    return dict(Counter(give_amounts))


# Example
if __name__ == "__main__":
    print(_split_banknotes_from_amount(50))
