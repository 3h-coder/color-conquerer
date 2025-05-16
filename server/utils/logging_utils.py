import logging

from flask import has_request_context, request

from config.variables import RequiredVariable


def flask_request_remote_addr_prefix():
    return request.remote_addr if has_request_context() else ""


def set_logging_level_from_config(logger: logging.Logger):
    # Call config here to avoid the following circular dependency :
    # config.logging -> utils.logging_utils (this file) -> config.config -> config.logging
    from config import config

    if config.get(RequiredVariable.DEBUG):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
