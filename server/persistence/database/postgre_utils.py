import logging

from sqlalchemy import create_engine

from config import config
from config.variables import RequiredVariable


def get_prostgre_uri():
    """
    Returns the PostgreSQL URI based on the environment variables
    """
    postgre_user = config.get(RequiredVariable.APP_POSTGRES_USER)
    postgre_password = config.get(RequiredVariable.APP_POSTGRES_PASSWORD)
    postgre_host = config.get(RequiredVariable.APP_POSTGRES_HOST)
    postgre_port = config.get(RequiredVariable.APP_POSTGRES_PORT)
    postgre_db_name = config.get(RequiredVariable.APP_POSTGRES_DB_NAME)

    return f"postgresql+psycopg2://{postgre_user}:{postgre_password}@{postgre_host}:{postgre_port}/{postgre_db_name}"


def check_postgre_connection(logger: logging.Logger = None):
    """
    Checks if the application can connect to the PostgreSQL database.
    Returns True if the connection is successful, False otherwise.
    """
    if logger:
        logger.info("Checking connection to the PostgreSQL database...")

    try:
        engine = create_engine(get_prostgre_uri())
        with engine.connect():
            if logger:
                logger.info("Successfully connected to the PostgreSQL database.")
            return True
    except Exception as ex:
        if logger:
            logger.error("Failed to connect to the PostgreSQL database.")
        raise
