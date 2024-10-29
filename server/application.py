from cachelib import FileSystemCache
from flask import Flask
from flask_cors import CORS
from flask_session import Session

from blueprints.home import home_bp
from blueprints.play import play_bp
from blueprints.session import session_bp
from config.config import default_config, global_config
from config.logging import get_configured_logger
from config.variables import OptionalVariables, RequiredVariables
from middlewares.error_handler import handle_error
from utils.os_utils import delete_file_or_folder


class Application(Flask):
    """
    Custom implementation of a flask application.
    """

    def __init__(self, import_name, **kwargs):
        self.logger = get_configured_logger(__name__)
        self.logger.debug("Initializing application")
        super().__init__(import_name, **kwargs)
        self.initialize()

    def initialize(self):
        self._clean_up()
        self._set_config()
        self._register_middlewares()
        self._register_blueprints()
        Session(self)
        CORS(self, supports_credentials=True)  # TODO: add the proper origins

    def _clean_up(self):
        """
        Code to be executed before initializing the app.
        Includes various clean ups.
        """
        # folder cleanup
        delete_session = self._get_from_config_or_default_config(
            OptionalVariables.RESET_SESSION_FILE_ON_STARTUP.name
        )
        if delete_session:
            self.logger.debug("Deleting session directory")
            delete_file_or_folder(
                self._get_from_config_or_default_config(
                    OptionalVariables.APP_SESSION_FILE_DIR.name
                )
            )

    def _set_config(self):
        """
        Sets the configuration of the flask application.

        Links
        - Flask config : https://flask.palletsprojects.com/en/latest/config
        - Flask session : https://flask-session.readthedocs.io/en/latest/config.html
        """
        self.config["SECRET_KEY"] = global_config[RequiredVariables.APP_SECRET_KEY.name]
        self.config["SESSION_COOKIE_SAMESITE"] = "None"
        self.config["SESSION_COOKIE_SECURE"] = True
        # self.config["SESSION_PERMANENT"] = True
        # self.config["PERMANENT_SESSION_LIFETIME"] = global_config[
        #     RequiredVariables.APP_SESSION_LIFETIME.name
        # ]
        self.config["SESSION_TYPE"] = "cachelib"
        app_session_file_dir = OptionalVariables.APP_SESSION_FILE_DIR.name
        self.config["SESSION_CACHELIB"] = FileSystemCache(
            cache_dir=self._get_from_config_or_default_config(app_session_file_dir),
            threshold=500,
        )

    def _register_middlewares(self):
        """
        Registers all the middlewares present in the middlewares package.
        """
        self.register_error_handler(Exception, handle_error)

    def _register_blueprints(self):
        """
        Registers all the blueprints present in the blueprints package
        """
        self.register_blueprint(session_bp)
        self.register_blueprint(home_bp)
        self.register_blueprint(play_bp)

    def _get_from_config_or_default_config(self, variable: str):
        return global_config.get(variable, default_config[variable])
