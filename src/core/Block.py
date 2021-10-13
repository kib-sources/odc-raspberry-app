from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json, LetterCase

RUSSIAN_RUBLE = 643


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Block(DataClassJsonMixin):
    # BankNote id
    bnid: str
    magic: str
    time: int
    uuid: str
    otok: str

    transaction_hash: str
    transaction_hash_signed: str = field(metadata=config(field_name="transactionHashSignature"))

    parent_uuid: Optional[str] = None
