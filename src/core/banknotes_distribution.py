from collections import Counter
from itertools import groupby
from operator import itemgetter
from typing import List, Dict

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
    print(f"Transferring {sum_}: {banknotes_to_give}")
    assert sum_ == amount, f"Not enough banknotes! Only {sum_} remaining, but {amount} needed. {banknotes_to_give}"

    return list(map(itemgetter(1), banknotes_to_give))


def _split_banknotes_from_amount(amount: int) -> Dict[int, int]:
    """
    Для заданной суммы выдаёт словарь {номинал: количество}.
    Алгоритм:
      1) Строит базовый пул cap[d] = next_denom//d - 1.
      2) В убывающем порядке берёт из этого пула до cap[d], пропуская d == amount.
      3) Если после шага 2 осталось rem>0, жадно добирает любые купюры без ограничения.
    Гарантируется, что 1-рублёвая купюра в пуле есть, так что rem в конце == 0.
    """
    possible = [1, 2, 5, 10, 50, 100, 500, 1000, 2000, 5000]

    # 1) считаем базовые «вместимости»
    cap: Dict[int, int] = {}
    for i in range(len(possible) - 1):
        d = possible[i]
        nxt = possible[i + 1]
        cap[d] = nxt // d - 1
    # для самого большого номинала cap не нужен (будем его пропускать, если d==amount)

    # 2) пробегаем по номиналам от большего к меньшему
    rem = amount
    result: Dict[int, int] = {}
    for d in sorted(possible, reverse=True):
        if d >= amount:
            # пропускаем купюру, равную сумме (чтобы, например, для 100 не давать одну 100-рублёвку),
            # и все ещё большие номиналы
            continue
        c = min(cap.get(d, 0), rem // d)
        if c:
            result[d] = c
            rem -= d * c

    # 3) если что-то не набрали — жадно «неограниченно»
    if rem > 0:
        for d in sorted(possible, reverse=True):
            if d > rem:
                continue
            c = rem // d
            result[d] = result.get(d, 0) + c
            rem -= d * c
            if rem == 0:
                break

    assert rem == 0, f"Не удалось разбить сумму {amount}"
    return result


# Example
if __name__ == "__main__":
    print(_split_banknotes_from_amount(50))
