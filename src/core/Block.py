from dataclasses import dataclass, field
from typing import Optional

from dataclasses_json import DataClassJsonMixin, config, dataclass_json, LetterCase

RUSSIAN_RUBLE = 643


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Block(DataClassJsonMixin):
    # BankNote id
    bnid: str
    magic: Optional[str]
    time: int
    uuid: str
    otok: str
    transaction_hash: Optional[str]
    transaction_hash_signed: Optional[str] = field(metadata=config(field_name="transactionHashSignature"))

    otok_signature: Optional[str] = None
    transaction_signature: Optional[str] = None
    parent_uuid: Optional[str] = None
