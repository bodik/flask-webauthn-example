"""fwe forms"""

from flask_wtf import FlaskForm
from wtforms import HiddenField, PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Length


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


class WebauthnRegisterForm(FlaskForm):
    """webauthn register token form"""

    attestation = HiddenField('Attestation', [InputRequired()])
    name = StringField('Name', [Length(max=250)])
    submit = SubmitField('Register', render_kw={'disabled': True})


class WebauthnLoginForm(FlaskForm):
    """webauthn login form"""

    assertion = HiddenField('Assertion', [InputRequired()])
