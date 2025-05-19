import os

from cachelib import FileSystemCache
from flask import Flask
from flask_cors import CORS
from flask_session import Session

from blueprints.home import home_bp
from blueprints.play import play_bp
from blueprints.session import session_bp
from config import config, runtime_test_data_path
from config.app_config import AppConfigKeys, AppSessionType
from config.logging import (
    enable_test_mode_for_logging,
    get_configured_logger,
    root_logger,
)
from config.variables import OptionalVariable, RequiredVariable
from middlewares.error_handler import handle_error
from utils import logging_utils, redis_utils
from utils.os_utils import delete_file_or_folder


class Application(Flask):
    """
    Custom implementation of a flask application.
    """

    TEST_SESSION_FILE_DIR = os.path.join(runtime_test_data_path, "session_data")

    def __init__(self, import_name, test_instance: bool = False, **kwargs):
        if test_instance:
            enable_test_mode_for_logging()

        self.logger = get_configured_logger(
            __name__,
            prefix_getter=lambda: logging_utils.flask_request_remote_addr_prefix(),
        )

        self.logger.info("Initializing the application")
        super().__init__(import_name, **kwargs)

        self.testing = test_instance

        self._initialize()
        logging_utils.set_logging_level_from_config(root_logger)

    def _initialize(self):
        self._clean_up()
        self._set_config()
        self._register_middlewares()
        self._register_blueprints()
        Session(self)
        if not self.testing:
            CORS(
                self,
                origins=config.get(RequiredVariable.CORS_ALLOWED_ORIGINS),
                supports_credentials=True,
            )

    def _clean_up(self):
        """
        Code to be executed before initializing the app.
        Includes various clean ups.
        """
        if self.testing:
            delete_file_or_folder(self.TEST_SESSION_FILE_DIR)
            return

        # folder cleanup
        delete_session = config.get(OptionalVariable.RESET_SESSION_FILE_ON_STARTUP)
        if delete_session:
            self.logger.debug("Deleting session directory")
            delete_file_or_folder(config.get(OptionalVariable.APP_SESSION_FILE_DIR))

    def _set_config(self):
        """
        Sets the configuration of the flask application.

        Resources
        - Flask config : https://flask.palletsprojects.com/en/latest/config
        - Flask session : https://flask-session.readthedocs.io/en/latest/config.html
        """
        if self.testing:
            self._set_testing_config()
        else:
            self._set_production_config()

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

    def _set_production_config(self):
        self.debug = config.get(RequiredVariable.DEBUG)
        # https://flask.palletsprojects.com/en/latest/config/#SECRET_KEY
        self.config[AppConfigKeys.SECRET_KEY] = config.get(
            RequiredVariable.APP_SECRET_KEY
        )
        # https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_SECURE
        # ⚠️ MUST be True
        self.config[AppConfigKeys.SESSION_COOKIE_SECURE] = True
        # https://flask.palletsprojects.com/en/latest/config/#SESSION_COOKIE_SAMESITE
        # ⚠️ MUST be "None" for the browser to accept cookie sending between the frontend and
        # the back-end, along with Secure=True (right above) and "credential":"include" in the frontend
        self.config[AppConfigKeys.SESSION_COOKIE_SAMESITE] = "None"

        # https://flask.palletsprojects.com/en/latest/config/#PERMANENT_SESSION_LIFETIME
        self.config[AppConfigKeys.PERMANENT_SESSION_LIFETIME] = config.get(
            RequiredVariable.APP_SESSION_LIFETIME_IN_S
        )
        # https://flask-session.readthedocs.io/en/latest/config.html#SESSION_KEY_PREFIX
        # Note : This is already the default, but we're making it explicit
        self.config[AppConfigKeys.SESSION_KEY_PREFIX] = "session:"
        if config.get(RequiredVariable.APP_REDIS_SESSION_STORAGE):
            self._set_up_redis_session()
        else:
            self._setup_file_system_session()

    def _set_testing_config(self):
        self.config[AppConfigKeys.SECRET_KEY] = "test_secret_key"
        self.config[AppConfigKeys.SESSION_TYPE] = AppSessionType.CACHELIB
        self.config[AppConfigKeys.SESSION_CACHELIB] = FileSystemCache(
            cache_dir=self.TEST_SESSION_FILE_DIR, threshold=20
        )
        self.config[AppConfigKeys.SESSION_PERMANENT] = False

    def _set_up_redis_session(self):
        """
        Will make the app store the session data on the running redis server.
        """
        if not redis_utils.is_redis_up_and_running(logger=self.logger):
            raise RuntimeError(
                "The app could not be initialized as it could not connect to the redis server"
            )

        self.config[AppConfigKeys.SESSION_TYPE] = AppSessionType.REDIS
        self.config[AppConfigKeys.SESSION_REDIS] = redis_utils.create_connection(
            logger=self.logger
        )

    def _setup_file_system_session(self):
        """
        Will make the app rely on a file system session.

        WARNING : This is handy in development but not recommended in production.
        """
        self.config[AppConfigKeys.SESSION_TYPE] = "cachelib"
        self.config[AppConfigKeys.SESSION_CACHELIB] = FileSystemCache(
            cache_dir=config.get(OptionalVariable.APP_SESSION_FILE_DIR),
            threshold=500,
        )
