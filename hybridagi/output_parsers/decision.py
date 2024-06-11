from .base import BaseOutputParser
from typing import List

class DecisionOutputParser(BaseOutputParser):
    """
    The output parser for decision making steps
    """

    def parse(self, output: str, options: List[str] = [], prefix:str = "") -> str:
        output = output.upper()
        output = output.replace("\\_", "_")
        output = output.replace("\_", "_")
        for opt in options:
            if output.find(opt) >= 0:
                return opt
        return output