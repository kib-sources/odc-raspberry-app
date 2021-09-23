from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional

RUSSIAN_RUBLE = 643


@dataclass_json
@dataclass
class OneBlock:
    # BankNote id
    bnid: str
    magic: str
    time: int
    uuid: str
    otok: str

    transaction_hash: str
    transaction_hash_signed: str
    parent_uuid: Optional[str] = None
