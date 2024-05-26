from flask import Flask
from flask_cors import CORS


class Application(Flask):
    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)
        self.initialize()

    def initialize(self):
        CORS(self, supports_credentials=True)
