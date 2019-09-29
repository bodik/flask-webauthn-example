"""fwe models"""

from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from fwe import db
from fwe.password_supervisor import PasswordSupervisor as PWS


class User(db.Model, UserMixin):
    """user model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    _password = db.Column(db.String(250), name='password')

    webauthn_credentials = relationship('WebauthnCredential', back_populates='user', cascade='delete,delete-orphan', passive_deletes=True)

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


class WebauthnCredential(db.Model):  # pylint: disable=too-few-public-methods
    """Webauthn credential model"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user_handle = db.Column(db.String(64), nullable=False)
    credential_data = db.Column(db.LargeBinary, nullable=False)
    name = db.Column(db.String(250))
    registered = db.Column(db.DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='webauthn_credentials')

    def __repr__(self):
        return '<WebauthnCredential %s: %s>' % (self.id, self.user_id)
