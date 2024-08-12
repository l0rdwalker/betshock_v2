import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from abstract_platform import platformManager

class betm(platformManager):
    def setPlatformName(self):
        self.name = 'betm'