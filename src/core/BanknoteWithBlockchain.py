from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from core.Banknote import Banknote
from core.Block import Block


@dataclass_json
@dataclass
class BanknoteWithBlockchain:
    banknote: Banknote
    blockchain: List[Block]
