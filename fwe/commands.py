"""fwe commands"""

import shutil

import click
from flask import current_app
from flask.cli import with_appcontext

from fwe import db
from fwe.models import User, WebauthnCredential  # noqa: F401  pylint: disable=unused-import


def db_remove():
    """remove database"""

    db.session.close()
    db.drop_all()
    shutil.rmtree(current_app.session_interface.storage, ignore_errors=True)


@click.command(name='dbinit')
@with_appcontext
def dbinit_command():  # pragma: no cover
    """initialize database schema"""

    db.create_all()
    db.session.add(User(username='fwe', password='fwe'))
    db.session.commit()


@click.command(name='dbremove')
@with_appcontext
def dbremove_command():
    """db remove command stub"""
    db_remove()
