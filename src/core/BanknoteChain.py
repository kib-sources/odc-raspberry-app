from dataclasses import dataclass
from typing import List

from core.Banknote import Banknote
from core.OneBlock import OneBlock


@dataclass
class BanknoteChain:
    banknote: Banknote
    blockchain: List[OneBlock]


