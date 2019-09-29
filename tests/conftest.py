"""fwe common pytest fixtures"""

import pytest
from fido2 import cbor
from soft_webauthn import SoftWebauthnDevice

from fwe import create_app, db, webauthn
from fwe.commands import db_remove
from fwe.models import User, WebauthnCredential
from fwe.password_supervisor import PasswordSupervisor as PWS
from tests import persist_and_detach


@pytest.fixture
def app():
    """yield application as pytest fixture"""

    _app = create_app('postgresql:///fwe_test', '/tmp/fwt_test_sessions')
    with _app.test_request_context():
        db_remove()
        db.create_all()
        yield _app
        db_remove()


@pytest.fixture
def test_user(app):  # pylint: disable=unused-argument,redefined-outer-name
    """persistent test user"""
    return persist_and_detach(User(username='user1', password=PWS().generate()))


@pytest.fixture
def test_wncred(test_user):  # pylint: disable=redefined-outer-name
    """persistent test registered webauthn credential"""

    device = SoftWebauthnDevice()
    device.cred_init(webauthn.rp.ident, b'randomhandle')
    wncred = WebauthnCredential(
        user_id=test_user.id,
        user=test_user,
        user_handle=device.user_handle,
        credential_data=cbor.encode(device.cred_as_attested().__dict__),
        name='testcredential')
    yield persist_and_detach(wncred)
