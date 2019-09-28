"""fwe selenium authentication tests"""

from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from fwe import db
from fwe.models import User
from fwe.password_supervisor import PasswordSupervisor as PWS
from tests.selenium import WEBDRIVER_WAIT


def test_login(live_server, selenium, test_user):  # pylint: disable=unused-argument
    """basic login test by username/password"""

    tmp_password = PWS().generate()
    tmp = User.query.filter(User.id == test_user.id).one_or_none()
    tmp.password = tmp_password
    db.session.commit()

    selenium.get(url_for('app.login_route', _external=True))
    selenium.find_element_by_xpath('//form//input[@name="username"]').send_keys(test_user.username)
    selenium.find_element_by_xpath('//form//input[@name="password"]').send_keys(tmp_password)
    selenium.find_element_by_xpath('//form//input[@type="submit"]').click()
    WebDriverWait(selenium, WEBDRIVER_WAIT).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Logout"]')))
