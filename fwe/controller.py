"""fwe controller"""

import string
from base64 import b64encode, b64decode
from http import HTTPStatus
from random import SystemRandom

from fido2 import cbor
from fido2.client import ClientData
from fido2.ctap2 import AttestationObject, AttestedCredentialData, AuthenticatorData
from flask import _request_ctx_stack, Blueprint, current_app, flash, g, redirect, render_template, request, Response, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from fwe import db, login_manager, webauthn
from fwe.forms import ButtonForm, LoginForm, UserForm, WebauthnLoginForm, WebauthnRegisterForm
from fwe.models import User, WebauthnCredential
from fwe.password_supervisor import PasswordSupervisor as PWS

blueprint = Blueprint('app', __name__)  # pylint: disable=invalid-name


# authentication

def regenerate_session():
    """regenerate session"""

    _request_ctx_stack.top.session = current_app.session_interface.new_session()
    if hasattr(g, 'csrf_token'):  # cleanup g, which is used by flask_wtf
        delattr(g, 'csrf_token')


@login_manager.user_loader
def user_loader(user_id):
    """flask_login user loader"""
    return User.query.filter(User.id == user_id).one_or_none()


@blueprint.route('/login', methods=['GET', 'POST'])
def login_route():
    """login route"""

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(User.username == form.username.data).one_or_none()
        if user:
            if form.password.data:
                # password authentication
                if PWS.compare(PWS.hash(form.password.data, PWS.get_salt(user.password)), user.password):
                    regenerate_session()
                    login_user(user)
                    return redirect(url_for('app.index_route'))
            elif user.webauthn_credentials:
                # webauthn authentication
                session['webauthn_login_user_id'] = user.id
                return redirect(url_for('app.webauthn_login_route', **request.args))

        flash('Invalid credentials.', 'error')

    return render_template('login.html', form=form)


@blueprint.route('/logout')
@login_required
def logout_route():
    """logout route"""

    logout_user()
    session.clear()
    return redirect(url_for('app.index_route'))


# webauthn authentication

@blueprint.route('/webauthn/list', methods=['GET'])
@login_required
def webauthn_list_route():
    """list registered credentials for current user"""

    creds = WebauthnCredential.query.all()
    return render_template('webauthn_list.html', creds=creds, button_form=ButtonForm())


@blueprint.route('/webauthn/delete/<webauthn_id>', methods=['POST'])
@login_required
def webauthn_delete_route(webauthn_id):
    """delete registered credential"""

    form = ButtonForm()
    if form.validate_on_submit():
        cred = WebauthnCredential.query.filter(WebauthnCredential.id == webauthn_id).one()
        db.session.delete(cred)
        db.session.commit()
        return redirect(url_for('app.webauthn_list_route'))

    return '', HTTPStatus.BAD_REQUEST


def webauthn_credentials(user):
    """get and decode all credentials for given user"""
    return [AttestedCredentialData.create(**cbor.decode(cred.credential_data)) for cred in user.webauthn_credentials]


def random_string(length=32):
    """generates random string"""
    return ''.join([SystemRandom().choice(string.ascii_letters + string.digits) for i in range(length)])


@blueprint.route('/webauthn/pkcco', methods=['POST'])
@login_required
def webauthn_pkcco_route():
    """get publicKeyCredentialCreationOptions"""

    form = ButtonForm()
    if form.validate_on_submit():
        user = User.query.get(current_user.id)
        user_handle = random_string()
        exclude_credentials = webauthn_credentials(user)
        pkcco, state = webauthn.register_begin(
            {'id': user_handle.encode('utf-8'), 'name': user.username, 'displayName': user.username},
            exclude_credentials)
        session['webauthn_register_user_handle'] = user_handle
        session['webauthn_register_state'] = state
        return Response(b64encode(cbor.encode(pkcco)).decode('utf-8'), mimetype='text/plain')

    return '', HTTPStatus.BAD_REQUEST


@blueprint.route('/webauthn/register', methods=['GET', 'POST'])
@login_required
def webauthn_register_route():
    """register credential for current user"""

    user = User.query.get(current_user.id)
    form = WebauthnRegisterForm()
    if form.validate_on_submit():
        try:
            attestation = cbor.decode(b64decode(form.attestation.data))
            auth_data = webauthn.register_complete(
                session.pop('webauthn_register_state'),
                ClientData(attestation['clientDataJSON']),
                AttestationObject(attestation['attestationObject']))

            db.session.add(WebauthnCredential(
                user_id=user.id,
                user_handle=session.pop('webauthn_register_user_handle'),
                credential_data=cbor.encode(auth_data.credential_data.__dict__),
                name=form.name.data))
            db.session.commit()

            return redirect(url_for('app.webauthn_list_route'))
        except (KeyError, ValueError) as e:
            current_app.logger.exception(e)
            flash('Error during registration.', 'error')

    return render_template('webauthn_register.html', form=form)


@blueprint.route('/webauthn/pkcro', methods=['POST'])
def webauthn_pkcro_route():
    """login webauthn pkcro route"""

    user = User.query.filter(User.id == session.get('webauthn_login_user_id')).one_or_none()
    form = ButtonForm()
    if user and form.validate_on_submit():
        pkcro, state = webauthn.authenticate_begin(webauthn_credentials(user))
        session['webauthn_login_state'] = state
        return Response(b64encode(cbor.encode(pkcro)).decode('utf-8'), mimetype='text/plain')

    return '', HTTPStatus.BAD_REQUEST


@blueprint.route('/webauthn/login', methods=['GET', 'POST'])
def webauthn_login_route():
    """webauthn login route"""

    user = User.query.filter(User.id == session.get('webauthn_login_user_id')).one_or_none()
    if not user:
        return login_manager.unauthorized()

    form = WebauthnLoginForm()
    if form.validate_on_submit():
        try:
            assertion = cbor.decode(b64decode(form.assertion.data))
            webauthn.authenticate_complete(
                session.pop('webauthn_login_state'),
                webauthn_credentials(user),
                assertion['credentialRawId'],
                ClientData(assertion['clientDataJSON']),
                AuthenticatorData(assertion['authenticatorData']),
                assertion['signature'])
            regenerate_session()
            login_user(user)
            return redirect(url_for('app.index_route'))

        except (KeyError, ValueError) as e:
            current_app.logger.exception(e)
            flash('Login error during Webauthn authentication.', 'error')

    return render_template('webauthn_login.html', form=form)


# application

@blueprint.route('/', methods=['GET'])
def index_route():
    """main index"""
    return render_template('index.html')


@blueprint.route('/user/list', methods=['GET'])
@login_required
def user_list_route():
    """users listing"""

    users = User.query.all()
    return render_template('user_list.html', users=users, button_form=ButtonForm())


@blueprint.route('/user/add', methods=['GET', 'POST'])
@login_required
def user_add_route():
    """add user"""

    form = UserForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('app.user_list_route'))

    return render_template('user_add.html', form=form)


@blueprint.route('/user/delete/<user_id>', methods=['POST'])
@login_required
def user_delete_route(user_id):
    """del user"""

    form = ButtonForm()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('app.user_list_route'))

    return '', HTTPStatus.BAD_REQUEST
