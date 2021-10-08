from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional

RUSSIAN_RUBLE = 643


@dataclass_json
@dataclass
class Block:
    # BankNote id
    bnid: str
    magic: str
    time: int
    uuid: str
    otok: str

    otok_signature: str
    transaction_signature: str
    parent_uuid: Optional[str] = None
