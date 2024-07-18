import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from abstract_platform import platformManager

class palmerbet(platformManager):
    def __init__(self) -> None:
        super().__init__()

    def setPlatformName(self):
        self.name = 'palmerbet'