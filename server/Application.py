from cachelib import FileSystemCache
from flask import Flask, session
from flask_cors import CORS
from flask_session import Session

from blueprints.play import play_bp
from blueprints.session import session_bp
from config.config import default_config, global_config
from config.logger import logger
from config.variables import OptionalVariables, RequiredVariables
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
        Session(self)
        CORS(self, supports_credentials=True)  # TODO: add the proper origins

    def set_config(self):
        """
        Sets the configuration of the flask application.

        Links
        - Flask config : https://flask.palletsprojects.com/en/latest/config
        - Flask session : https://flask-session.readthedocs.io/en/latest/config.html
        """
        self.config["SECRET_KEY"] = global_config[RequiredVariables.APP_SECRET_KEY.name]
        # self.config["SESSION_PERMANENT"] = True
        # self.config["PERMANENT_SESSION_LIFETIME"] = global_config[
        #     RequiredVariables.APP_SESSION_LIFETIME.name
        # ]
        # self.config["SESSION_COOKIE_SAMESITE"] = "None"
        self.config["SESSION_TYPE"] = "cachelib"
        # self.config["SESSION_SERIALIZATION_FORMAT"] = "json"

        app_session_file_dir = OptionalVariables.APP_SESSION_FILE_DIR.name
        self.config["SESSION_CACHELIB"] = FileSystemCache(
            cache_dir=self.get_from_config_or_default_config(app_session_file_dir),
            threshold=500,
        )

    def register_middlewares(self):
        """
        Registers all the middlewares present in the middlewares package.
        """
        self.register_error_handler(Exception, handle_error)

    def register_blueprints(self):
        """
        Registers all the blueprints present in the blueprints package
        """
        self.register_blueprint(session_bp)
        self.register_blueprint(play_bp)

    def get_from_config_or_default_config(self, variable: str):
        return global_config.get(variable, default_config[variable])
