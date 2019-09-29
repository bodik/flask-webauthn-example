"""fwe authentication routes tests"""

from http import HTTPStatus

from flask import url_for

from fwe import db
from fwe.models import User
from fwe.password_supervisor import PasswordSupervisor as PWS


def test_login_route(client, test_user):
    """test login route"""

    tmp_password = PWS().generate()
    tmp = User.query.filter(User.id == test_user.id).one_or_none()
    tmp.password = tmp_password
    db.session.commit()

    form = client.get(url_for('app.login_route')).form
    form['username'] = test_user.username
    form['password'] = 'invalid'
    response = form.submit()
    assert response.status_code == HTTPStatus.OK
    assert response.lxml.xpath('//script[contains(text(), "toastr[\'error\'](\'Invalid credentials.\');")]')

    form = client.get(url_for('app.login_route')).form
    form['username'] = test_user.username
    form['password'] = tmp_password
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND

    response = client.get(url_for('app.index_route'))
    assert response.lxml.xpath('//a[text()="Logout"]')


def test_logout_route(cl_user):
    """test logout"""

    response = cl_user.get(url_for('app.logout_route'))
    assert response.status_code == HTTPStatus.FOUND
    response = response.follow()
    assert response.lxml.xpath('//a[text()="Login"]')


def test_not_logged_in(client):
    """test for not logged in"""

    response = client.get(url_for('app.logout_route'))
    assert response.status_code == HTTPStatus.FOUND
    response = response.follow()
    assert response.lxml.xpath('//script[contains(text(), "toastr[\'warning\'](\'Not logged in\');")]')
