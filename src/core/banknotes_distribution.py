from itertools import groupby
from operator import itemgetter
from typing import List

from core.BanknoteWithBlockchain import BanknoteWithBlockchain


def select_banknotes_from_bag(bag: List[BanknoteWithBlockchain], amount: int):
    give_amounts = _split_bucks_from_amount(amount)

    banknotes_in_wallet = [(it.banknote.amount, idx) for idx, it in enumerate(bag)]

    banknotes_to_give = list()
    for key, group in groupby(banknotes_in_wallet, lambda it: it[0]):
        if key in give_amounts.keys():
            banknotes_to_give += list(group)[:give_amounts[key]]

    assert sum(map(itemgetter(0), banknotes_to_give)) < amount, f"Not enough bucks! Only {sum(map(itemgetter(0), banknotes_to_give))} gathered"

    return list(map(itemgetter(1), banknotes_to_give))


def _split_bucks_from_amount(amount: int):
    give_amounts = dict()

    banknote_amounts = [
        [1, 30], [2, 30], [5, 10],
        [10, 10], [50, 10],
        [100, 10], [500, 10],
        [1000, 10], [2000, 10], [5000, 10]
    ]

    is_forward = True
    while True:
        for banknote_amount in banknote_amounts:
            count = amount // banknote_amount[0]

            if count > banknote_amount[1]:
                count = banknote_amount[1]

            if count == 0:
                continue

            if banknote_amount[0] not in give_amounts:
                give_amounts[banknote_amount[0]] = count
            else:
                give_amounts[banknote_amount[0]] += count

            amount -= count * banknote_amount[0]
            if amount == 0:
                break

        if amount == 0:
            break

        if is_forward:
            is_forward = False
            banknote_amounts = list(reversed(banknote_amounts))

    return give_amounts


# Example
if __name__ == "__main__":
    print(_split_bucks_from_amount(1000))
