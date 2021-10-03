from dataclasses import dataclass
from typing import List

from core.Banknote import Banknote
from core.Block import Block


@dataclass
class BanknoteWithBlockchain:
    banknote: Banknote
    blockchain: List[Block]


