"""fwe app pytest setup and fixtures"""

import pytest
from flask import url_for
from webtest import TestApp

from fwe import db
from fwe.models import User
from fwe.password_supervisor import PasswordSupervisor as PWS


@pytest.fixture
def runner(app):  # pylint: disable=redefined-outer-name
    """create cli test runner"""
    return app.test_cli_runner()


@pytest.fixture
def client(app):  # pylint: disable=redefined-outer-name
    """create webtest testapp client"""
    return TestApp(app)


@pytest.fixture
def cl_user(client):  # pylint: disable=redefined-outer-name
    """yield authenticated client"""

    tmp_password = PWS().generate()
    tmp_user = User(username='pytest_user', password=tmp_password)
    db.session.add(tmp_user)
    db.session.commit()

    form = client.get(url_for('app.login_route')).form
    form['username'] = tmp_user.username
    form['password'] = tmp_password
    form.submit()
    return client
