"""fwe selenium basic tests"""

from flask import url_for


def test_index_route(live_server, selenium):  # pylint: disable=unused-argument
    """very basic index hit test"""

    selenium.get(url_for('app.index_route', _external=True))
    assert '- Flask Webauthn Example' in selenium.title
