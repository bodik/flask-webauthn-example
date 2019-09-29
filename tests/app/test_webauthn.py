"""fwe webauthn related routes tests"""

from base64 import b64encode, b64decode
from http import HTTPStatus

from fido2 import cbor
from flask import url_for
from soft_webauthn import SoftWebauthnDevice

from fwe import webauthn
from fwe.models import User, WebauthnCredential
from tests.app import get_csrf_token


def test_webauthn_list_route(cl_user, test_wncred):
    """list webauthn credentials route test"""

    response = cl_user.get(url_for('app.webauthn_list_route'))
    assert response.status_code == HTTPStatus.OK
    assert '<td>%s</td>' % test_wncred.user_handle in response


def test_webauthn_delete_route(cl_user, test_wncred):
    """delete webauthn credentials route test"""

    response = cl_user.post(url_for('app.webauthn_delete_route', webauthn_id=test_wncred.id), status='*')
    assert response.status_code == HTTPStatus.BAD_REQUEST

    response = cl_user.post(
        url_for('app.webauthn_delete_route', webauthn_id=test_wncred.id),
        {'csrf_token': get_csrf_token(cl_user)}
    )
    assert response.status_code == HTTPStatus.FOUND
    assert not WebauthnCredential.query.filter(WebauthnCredential.id == test_wncred.id).one_or_none()


def test_webauthn_register_route(cl_user):
    """register new credential for user"""

    device = SoftWebauthnDevice()

    response = cl_user.get(url_for('app.webauthn_register_route'))
    # some javascript code must be emulated
    pkcco = cbor.decode(b64decode(cl_user.post(url_for('app.webauthn_pkcco_route'), {'csrf_token': get_csrf_token(cl_user)}).body))
    attestation = device.create(pkcco, 'https://%s' % webauthn.rp.ident)
    attestation_data = {
        'clientDataJSON': attestation['response']['clientDataJSON'],
        'attestationObject': attestation['response']['attestationObject']}
    form = response.form
    form['attestation'] = b64encode(cbor.encode(attestation_data))
    # and back to standard test codeflow
    form['name'] = 'pytest token'
    response = form.submit()

    assert response.status_code == HTTPStatus.FOUND
    user = User.query.filter(User.username == 'pytest_user').one()
    assert user.webauthn_credentials


def test_webauthn_pkcco_route_invalid_request(cl_user):
    """test error handling in pkcco route"""

    response = cl_user.post(url_for('app.webauthn_pkcco_route'), status='*')
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_webauthn_register_route_invalid_attestation(cl_user):
    """register new credential for user; error handling"""

    form = cl_user.get(url_for('app.webauthn_register_route')).form
    form['attestation'] = 'invalid'
    response = form.submit()
    assert response.status_code == HTTPStatus.OK
    assert response.lxml.xpath('//script[contains(text(), "toastr[\'error\'](\'Error during registration.\');")]')
