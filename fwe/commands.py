"""fwe commands"""

import click
from flask.cli import with_appcontext

from . import db
from .models import User


def db_remove():
    """remove database"""

    db.session.close()
    db.drop_all()


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
