"""fwe common pytest fixtures"""

import pytest

from fwe import create_app, db
from fwe.commands import db_remove


@pytest.fixture
def app():
    """yield application as pytest fixture"""

    _app = create_app('postgresql:///fwe_test', '/tmp/fwt_test_sessions')
    with _app.test_request_context():
        db_remove()
        db.create_all()
        yield _app
        db_remove()
