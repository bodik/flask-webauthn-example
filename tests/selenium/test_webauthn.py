"""fwe selenium webauthn related routes tests"""

from base64 import b64decode, b64encode

from fido2 import cbor
from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from soft_webauthn import SoftWebauthnDevice

from fwe import webauthn
from fwe.models import User, WebauthnCredential
from tests import persist_and_detach
from tests.selenium import js_variable_ready, WEBDRIVER_WAIT


def test_webauthn_register_route(live_server, sl_user):  # pylint: disable=unused-argument
    """register new credential for user"""

    device = SoftWebauthnDevice()

    sl_user.get(url_for('app.webauthn_register_route', _external=True))
    # some javascript code must be emulated
    WebDriverWait(sl_user, WEBDRIVER_WAIT).until(js_variable_ready('window.pkcco_raw'))
    pkcco = cbor.decode(b64decode(sl_user.execute_script('return window.pkcco_raw;').encode('utf-8')))
    attestation = device.create(pkcco, 'https://%s' % webauthn.rp.ident)
    sl_user.execute_script('pack_attestation(CBOR.decode(base64_to_array_buffer("%s")));' % b64encode(cbor.encode(attestation)).decode('utf-8'))
    # and back to standard test codeflow
    sl_user.find_element_by_xpath('//form[@id="webauthn_register_form"]//input[@name="name"]').send_keys('pytest token')
    sl_user.find_element_by_xpath('//form[@id="webauthn_register_form"]//input[@type="submit"]').click()

    user = User.query.filter(User.username == 'pytest_user').one()
    assert user.webauthn_credentials


def test_login_webauthn(live_server, selenium, test_user):  # pylint: disable=unused-argument
    """test login by webauthn"""

    device = SoftWebauthnDevice()
    device.cred_init(webauthn.rp.ident, b'randomhandle')
    persist_and_detach(WebauthnCredential(
        user_handle=device.user_handle,
        user=test_user,
        credential_data=cbor.encode(device.cred_as_attested().__dict__)))

    selenium.get(url_for('app.login_route', _external=True))
    selenium.find_element_by_xpath('//form//input[@name="username"]').send_keys(test_user.username)
    selenium.find_element_by_xpath('//form//input[@type="submit"]').click()

    # some javascript code must be emulated
    WebDriverWait(selenium, WEBDRIVER_WAIT).until(js_variable_ready('window.pkcro_raw'))
    pkcro = cbor.decode(b64decode(selenium.execute_script('return window.pkcro_raw;').encode('utf-8')))
    assertion = device.get(pkcro, 'https://%s' % webauthn.rp.ident)
    selenium.execute_script('authenticate_assertion(CBOR.decode(base64_to_array_buffer("%s")));' % b64encode(cbor.encode(assertion)).decode('utf-8'))
    # and back to standard test codeflow

    WebDriverWait(selenium, WEBDRIVER_WAIT).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Logout"]')))
