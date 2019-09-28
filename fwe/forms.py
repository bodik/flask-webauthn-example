"""fwe forms"""

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired


class ButtonForm(FlaskForm):
    """only button form"""


class LoginForm(FlaskForm):
    """login form"""

    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Login')


class UserForm(FlaskForm):
    """user form"""

    username = StringField('Username', [InputRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Save')
