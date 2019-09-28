"""fwe basic tests"""

from http import HTTPStatus

from flask import url_for

from fwe.models import User
from tests.app import get_csrf_token


def test_index_route(client):
    """test root url"""

    response = client.get(url_for('app.index_route'))
    assert response.status_code == HTTPStatus.OK


def test_user_list_route(cl_user, test_user):
    """test user listing"""

    response = cl_user.get(url_for('app.user_list_route'))
    assert response.status_code == HTTPStatus.OK
    assert '<td>%s</td>' % test_user.username in response


def test_user_add_route(cl_user):
    """test user add"""

    form = cl_user.get(url_for('app.user_add_route')).form
    form['username'] = 'test_user_add'
    form['password'] = 'test_user_add'
    response = form.submit()
    assert response.status_code == HTTPStatus.FOUND
    assert User.query.filter(User.username == 'test_user_add').one()


def test_user_delete_route(cl_user, test_user):
    """test user add"""

    response = cl_user.post(url_for('app.user_delete_route', user_id=test_user.id), status='*')
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = cl_user.post(
        url_for('app.user_delete_route', user_id=test_user.id),
        {'csrf_token': get_csrf_token(cl_user)}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert not User.query.filter(User.id == test_user.id).one_or_none()
