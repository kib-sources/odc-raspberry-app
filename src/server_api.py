from typing import Optional

import requests

from core.Banknote import Banknote
from core.BanknoteChain import BanknoteChain
from core.OneBlock import OneBlock
from core.crypto import hash_items, sign_with_private_key, init_pair
from core.utils import current_epoch_time, random_numerical_string

server_url = "http://31.186.250.158"


def register_wallet(sok: str):
    register_response = requests.post(f"{server_url}/register-wallet", json={"sok": sok})
    register_response_code = register_response.status_code

    if register_response_code == 409:
        print("Этот sok уже используется, необходимо сбросить базу данных или использовать другой.")
        return

    if register_response_code == 400:
        print("sok не является RSA-ключем правильного формата")
        return

    register_response_json = register_response.json()

    # Дополнаяем доступные данные
    sok_signature = register_response_json["sok_signature"]
    wid = register_response_json["wid"]
    return wid


def issue_and_receive_banknotes(amount_to_issue: int, wid: str, spk: str) -> Optional[list]:
    # One Time Open Key RSA-ключ, для простоты будем использовать один ключ для всех банкнот
    otok = """-----BEGIN RSA PUBLIC KEY-----
    MEgCQQC5ohEmk4zwb6YdoBrWjkCr/1ZLc729AYc7QC8sabaSLiujiRcd6VwL7drxQJymxN/gHrvHYDU1xxtiuYCk7nF7AgMBAAE=
    -----END RSA PUBLIC KEY-----"""

    # Для получения банкнот их необходимо выпустить
    issue_response = requests.post(f"{server_url}/issue-banknotes",
                                   json={"amount": amount_to_issue, "wid": wid})
    issue_response_code = issue_response.status_code

    if issue_response_code == 400:
        print("wid не был найден в базе данных")
        return

    issue_response_json = issue_response.json()

    # Дополняем доступные данные
    issued_banknotes = issue_response_json["issued_banknotes"]

    print(f"Выпущено(-а) {len(issued_banknotes)} банкнот(-а)")

    # Регистрируем каждую выпущенную банкноту
    banknote_initial_chains = list()
    for i, banknote in enumerate(issued_banknotes):
        # Идентификатор банкноты
        bnid = banknote["bnid"]
        # Подписываем хэш otok клиентским spk, это необходимо чтобы гарантировать подлинность otok
        otok_hash = hash_items([otok])
        otok_signature = sign_with_private_key(otok_hash, spk)
        # Выбираем текущее время как время транзакции
        current_time = current_epoch_time()
        # Случайный уникальный идентификатор
        uuid = random_numerical_string(12)
        # Хэш параметров транзакции, подписанный spk, это необходимо чтобы гарантировать валидность операции
        transaction_hash = hash_items([uuid, otok, bnid, current_time])
        transaction_signature = sign_with_private_key(transaction_hash, spk)

        banknote_initial_chain = {"bnid": bnid, "otok": otok, "wid": wid, "time": current_time, "uuid": uuid,
                                  "otok_signature": otok_signature, "transaction_signature": transaction_signature}
        banknote_initial_chains.append(banknote_initial_chain)

    receive_response = requests.post(f"{server_url}/receive-banknotes",
                                     json={"wid": wid, "banknotes": banknote_initial_chains})
    receive_code = receive_response.status_code

    if receive_code != 200:
        print("Не удалось получить банкноты")
        return

    receive_json = receive_response.json()

    rejected_banknotes = receive_json["rejected_banknotes"]
    if len(rejected_banknotes) != 0:
        print(f"Ошибка при получении банкнот(-ы)")
        for rejected_banknote_details in rejected_banknotes:
            print(rejected_banknote_details)

    blockchains = [{**it[0], **it[1]} for it in zip(banknote_initial_chains, receive_json["received_banknotes"])]
    banknotes_with_chain = zip(issued_banknotes, blockchains)

    return [BanknoteChain(
        banknote=Banknote.from_dict(it[0]),
        blockchain=[OneBlock.from_dict(it[1])]
    ) for it in banknotes_with_chain]


# Example
if __name__ == "__main__":
    sok_, spk_ = init_pair()

    # Перед началом работы регистрируем кошелек на сервере
    wid_ = register_wallet(sok_)
    print("wid", wid_)

    banknotes = issue_and_receive_banknotes(10, wid_, spk_)
    for banknote in banknotes:
        print(banknote)
