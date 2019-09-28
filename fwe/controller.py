"""fwe controller"""

from http import HTTPStatus

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user

from . import db, login_manager
from .forms import ButtonForm, LoginForm, UserForm
from .models import User
from .password_supervisor import PasswordSupervisor as PWS

blueprint = Blueprint('app', __name__)  # pylint: disable=invalid-name


# authentication

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
                if PWS.compare(PWS.hash(form.password.data, PWS.get_salt(user.password)), user.password):
                    # TODO: regenerate session
                    login_user(user)
                    return redirect(url_for('app.index_route'))

        flash('Invalid credentials.', 'error')

    return render_template('login.html', form=form)


@blueprint.route('/logout')
@login_required
def logout_route():
    """logout route"""

    logout_user()
    # TODO: regenerate session
    return redirect(url_for('app.index_route'))


# application

@blueprint.route('/', methods=['GET'])
def index_route():
    """main index"""
    return render_template('index.html')


@blueprint.route('/user/list', methods=['GET', 'POST'])
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
