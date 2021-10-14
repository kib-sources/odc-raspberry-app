from typing import List, Union
from typing import Optional
from uuid import UUID

import requests

from core import crypto
from core.Banknote import Banknote
from core.BanknoteWithBlockchain import BanknoteWithBlockchain
from core.Block import Block
from core.crypto import hash_items, sign_with_private_key
from core.utils import current_epoch_time, gen_uuid

server_url = "http://31.186.250.158"


class Wallet:
    spk: str  # SIM Private key
    sok: str  # SIM Open key
    sok_signature: str
    wid: str  # wallet id
    banknotes: List[BanknoteWithBlockchain]

    def __init__(self):
        self.sok, self.spk = crypto.init_pair()
        self._register()
        self.banknotes = list()
        self._bag = dict()

    def refill(self, amount: int):
        banknotes: Optional[list] = self._issue_and_receive_banknotes(amount)
        self.banknotes += banknotes

    def deposit_amount(self):
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

    def _register(self) -> (str, str):
        register_response = requests.post(f"{server_url}/register-wallet", json={"sok": self.sok})

        if register_response.status_code == 409:
            print("Этот sok уже используется, необходимо сбросить базу данных или использовать другой.")
            return

        if register_response.status_code == 400:
            print("sok не является RSA-ключем правильного формата")
            return

        register_response_json = register_response.json()

        # Дополнаяем доступные данные
        self.sok_signature = register_response_json["sok_signature"]
        self.wid = register_response_json["wid"]

    def _issue_and_receive_banknotes(self, amount_to_issue: int) -> Optional[list]:
        # One Time Open Key RSA-ключ, для простоты будем использовать один ключ для всех банкнот
        otok, otpk = crypto.init_pair()

        # Для получения банкнот их необходимо выпустить
        js = {"amount": amount_to_issue, "wid": self.wid}
        issue_response = requests.post(f"{server_url}/issue-banknotes", json=js)
        if issue_response.status_code == 400:
            print("wid не был найден в базе данных")
            return

        issue_response_json = issue_response.json()
        issued_banknotes = issue_response_json["issued_banknotes"]
        print(f"Выпущено(-а) {len(issued_banknotes)} банкнот(-а)")

        # Регистрируем каждую выпущенную банкноту
        banknotes_initial_chains = list()
        for banknote in issued_banknotes:
            banknote_initial_chain = self._register_banknote(banknote, otok, otpk)
            banknotes_initial_chains.append(banknote_initial_chain)

        # Получение банкнот
        js = {"wid": self.wid, "banknotes": banknotes_initial_chains}
        receive_response = requests.post(f"{server_url}/receive-banknotes", json=js)
        if receive_response.status_code != 200:
            print("Не удалось получить банкноты")
            return

        receive_json = receive_response.json()
        rejected_banknotes = receive_json["rejected_banknotes"]
        if len(rejected_banknotes) != 0:
            print(f"Ошибка при получении банкнот(-ы)")
            for rejected_banknote_details in rejected_banknotes:
                print(rejected_banknote_details)

        blockchains = [{**it[0], **it[1]} for it in zip(banknotes_initial_chains, receive_json["received_banknotes"])]
        banknotes_with_chain = zip(issued_banknotes, blockchains)

        return [BanknoteWithBlockchain(
            banknote=Banknote.from_dict(it[0]),
            blocks=[Block.from_dict(it[1])]
        ) for it in banknotes_with_chain]

    def _register_banknote(self, banknote, otok, otpk) -> dict:
        # Идентификатор банкноты
        bnid = banknote["bnid"]

        # Подписываем хэш otok клиентским spk, это необходимо чтобы гарантировать подлинность otok
        otok_hash = hash_items([otok])
        otok_signature = sign_with_private_key(otok_hash, self.spk)

        # Выбираем текущее время как время транзакции
        current_time = current_epoch_time()

        # Случайный уникальный идентификатор
        uuid_ = gen_uuid()
        self._bag[uuid_] = otpk

        # Хэш параметров транзакции, подписанный spk, это необходимо чтобы гарантировать валидность операции
        transaction_hash = hash_items([uuid_, otok, bnid, current_time])
        transaction_signature = sign_with_private_key(transaction_hash, self.spk)

        banknote_initial_chain = {
            "bnid": bnid,
            "otok": otok,
            "wid": self.wid,
            "time": current_time,
            "uuid": uuid_,
            "otok_signature": otok_signature,
            "transaction_signature": transaction_signature
        }
        return banknote_initial_chain

    @staticmethod
    def get_bank_info() -> (str, str):
        bok_response = requests.get(f"{server_url}/credentials")
        bok_response_json = bok_response.json()
        bin_ = bok_response_json["bin"]
        bok_ = bok_response_json["bok"]
        return int(bin_), bok_


# Example
if __name__ == "__main__":
    wallet_ = Wallet()
    wallet_.refill(300)
    wallet_.refill(25)

    print("$", wallet_.deposit_amount())
    print(len(wallet_.banknotes), "банкнот")
