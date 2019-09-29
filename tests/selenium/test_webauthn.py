"""fwe selenium webauthn related routes tests"""

from base64 import b64decode, b64encode

from fido2 import cbor
from flask import url_for
from selenium.webdriver.support.ui import WebDriverWait
from soft_webauthn import SoftWebauthnDevice

from fwe import webauthn
from fwe.models import User
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
