"""fwe models"""

from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from . import db
from .password_supervisor import PasswordSupervisor as PWS


class User(db.Model, UserMixin):
    """user model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    _password = db.Column(db.String(250), name='password')

    @hybrid_property
    def password(self):
        """password getter"""
        return self._password

    @password.setter
    def password(self, value):
        """password setter; condition is handling value edit from empty form.populate_obj submission"""

        if value:
            self._password = PWS().hash(value)

    def __repr__(self):
        return '<User %s: %s>' % (self.id, self.username)
