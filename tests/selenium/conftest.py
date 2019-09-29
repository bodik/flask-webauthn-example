"""fwe selenium pytest setup and fixtures"""

import pytest
from flask import url_for
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from fwe import db
from fwe.models import User
from fwe.password_supervisor import PasswordSupervisor as PWS
from tests.selenium import WEBDRIVER_WAIT


@pytest.fixture
def firefox_options(firefox_options):  # pylint: disable=redefined-outer-name
    """override firefox options"""

    firefox_options.headless = True
    return firefox_options


@pytest.fixture
def sl_user(selenium):  # pylint: disable=redefined-outer-name
    """yield authenticated selenium"""

    tmp_password = PWS().generate()
    tmp_user = User(username='pytest_user', password=tmp_password)
    db.session.add(tmp_user)
    db.session.commit()

    selenium.get(url_for('app.login_route', _external=True))
    selenium.find_element_by_xpath('//form//input[@name="username"]').send_keys(tmp_user.username)
    selenium.find_element_by_xpath('//form//input[@name="password"]').send_keys(tmp_password)
    selenium.find_element_by_xpath('//form//input[@type="submit"]').click()
    WebDriverWait(selenium, WEBDRIVER_WAIT).until(EC.presence_of_element_located((By.XPATH, '//a[text()="Logout"]')))

    yield selenium
