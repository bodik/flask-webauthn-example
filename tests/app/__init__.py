"""app tests module (and shared functions)"""

from flask import url_for


def get_csrf_token(client):
    """fetch index and parse csrf token"""

    response = client.get(url_for('app.index_route'))
    return response.lxml.xpath('//meta[@name="csrf-token"]/@content')[0]
