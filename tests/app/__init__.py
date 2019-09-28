"""misc tests functions"""

from flask import url_for

from fwe import db


def persist_and_detach(model):
    """would persist entity/model and detach. used for testing"""

    db.session.add(model)
    db.session.commit()
    db.session.refresh(model)
    db.session.expunge(model)
    return model


def get_csrf_token(client):
    """fetch index and parse csrf token"""

    response = client.get(url_for('app.index_route'))
    return response.lxml.xpath('//meta[@name="csrf-token"]/@content')[0]
