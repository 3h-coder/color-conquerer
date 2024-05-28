from flask import Flask


class Application(Flask):
    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)
        self.initialize()

    def initialize(self):
        pass
