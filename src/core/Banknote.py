from dataclasses import dataclass
from dataclasses_json import dataclass_json
from core import crypto

RUSSIAN_RUBLE = 643


@dataclass_json
@dataclass
class Banknote:
    # BankNote id
    bnid: str
    bin: int
    amount: int
    code: int
    signature: str
    time: int
    code: int

    @classmethod
    def make_hash(cls, *, bnid):
        return crypto.hash_(bnid)

    def verify(self, bok):
        _hash = Banknote.make_hash(bnid=self.bnid)
        if _hash != self.hash:
            return False
        if not crypto.verify_signature(self.hash, self.signature, bok):
            return False
        return True


if __name__ == "__main__":
    js = {
        'amount': 1,
        'bin': '1111',
        'bnid': '614c85326ff0d04ec67d9f49',
        'code': 643,
        'signature': '13c00e71b1a1d8c89d950fa29306ff9d8c3bc3372ccb4bc9b8f93efcbd8b284d2d41c717a5aa1e0aa580063a831fd7333d61983f477376e07ec4e5ae482d4c08',
        'time': 1632404786
    }
    print(Banknote.from_dict(js))
