"""fwe selenium tests"""

import pytest


@pytest.fixture
def firefox_options(firefox_options):  # pylint: disable=redefined-outer-name
    """override firefox options"""

    firefox_options.headless = True
    return firefox_options
