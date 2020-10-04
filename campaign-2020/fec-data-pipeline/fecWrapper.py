import os

class fecWrapper:

    def __init__(self):
        self.api_key = os.environ.get('FEC_KEY', None)

