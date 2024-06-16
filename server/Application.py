from flask import Flask

from blueprints.play import play_bp
from config.config import global_config
from config.logger import logger
from config.variables import RequiredVariables
from middlewares.error_handler import handle_error


class Application(Flask):
    """
    Custom implementation of a flask application.
    """

    def __init__(self, import_name, **kwargs):
        logger.debug("Initializing application")
        super().__init__(import_name, **kwargs)
        self.initialize()

    def initialize(self):
        self.set_config()
        self.register_middlewares()
        self.register_blueprints()

    def set_config(self):
        self.config["SECRET_KEY"] = global_config[RequiredVariables.APP_SECRET_KEY.name]

    def register_middlewares(self):
        """
        Registers all the middlewares present in the middlewares package.
        """
        self.register_error_handler(Exception, handle_error)

    def register_blueprints(self):
        """
        Registers all the blueprints present in the blueprints package
        """
        self.register_blueprint(play_bp)
