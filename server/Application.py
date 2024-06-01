from flask import Flask


class Application(Flask):
    """
    Custom implementation of a flask application.
    """

    def __init__(self, import_name, **kwargs):
        super().__init__(import_name, **kwargs)
        self.initialize()

    def initialize(self):
        self.set_config()

    def set_config(self):
        self.config["SECRET_KEY"] = "your_secret_key_here"
