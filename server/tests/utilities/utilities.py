"""
Utility methods for test setup and execution.
"""

from flask.testing import FlaskClient


def initialize_session(flask_test_client: FlaskClient):
    response = flask_test_client.get("/session")
    assert response.status_code == 200
