"""fwe selenium tests"""

import pytest

from tests.app.conftest import test_user  # noqa: F401  pylint: disable=unused-import


@pytest.fixture
def firefox_options(firefox_options):  # pylint: disable=redefined-outer-name
    """override firefox options"""

    firefox_options.headless = True
    return firefox_options
