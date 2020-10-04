import datadotworld as dw
import os

class dataDotWorld:

    def __init__(self):
        self.api_key = os.environ.get('DW_AUTH', None)

