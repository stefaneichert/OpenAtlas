import importlib
from typing import Union

import bcrypt
from flask import flash, g, render_template, session, url_for
from flask_babel import lazy_gettext as _
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from werkzeug.wrappers import Response
from wtforms import BooleanField, PasswordField, SubmitField
from wtforms.validators import InputRequired

from openatlas import app
from openatlas.database.connect import Transaction
from openatlas.display.tab import Tab
from openatlas.display.util import (
    button, display_form, display_info, manual, uc_first)
from openatlas.forms.setting import DisplayForm, ModulesForm, ProfileForm
from openatlas.forms.util import get_form_settings, set_form_settings


class PasswordForm(FlaskForm):
    password_old = PasswordField(_('old password'), [InputRequired()])
    password = PasswordField(_('password'), [InputRequired()])
    password2 = PasswordField(_('repeat password'), [InputRequired()])
    show_passwords = BooleanField(_('show passwords'))
    save = SubmitField(_('save'))

    def validate(self) -> bool:
        valid = FlaskForm.validate(self)
        hash_ = bcrypt.hashpw(
            self.password_old.data.encode('utf-8'),
            current_user.password.encode('utf-8'))
        if hash_ != current_user.password.encode('utf-8'):
            self.password_old.errors.append(_('error wrong password'))
            valid = False
        if self.password.data != self.password2.data:
            self.password.errors.append(_('error passwords must match'))
            self.password2.errors.append(_('error passwords must match'))
            valid = False
        if self.password_old.data == self.password.data:
            self.password.errors.append(
                _('error new password like old password'))
            valid = False
        if len(self.password.data) < g.settings['minimum_password_length']:
            self.password.errors.append(_('error password too short'))
            valid = False
        return valid


@app.route('/profile', methods=['POST', 'GET'])
@login_required
def profile_index() -> str:
    tabs = {
        'profile': Tab(
            'profile',
            display_info(get_form_settings(ProfileForm(), True)),
            buttons=[manual('tools/profile')]),
        'modules': Tab(
            'modules',
            display_info(get_form_settings(ModulesForm(), True)),
            buttons=[manual('tools/profile')]),
        'display': Tab(
            'display',
            display_info(get_form_settings(DisplayForm(), True)),
            buttons=[manual('tools/profile')])}
    if not app.config['DEMO_MODE']:
        tabs['profile'].buttons += [
            button(_('edit'), url_for('profile_settings', category='profile')),
            button(_('change password'), url_for('profile_password'))]
        tabs['modules'].buttons.append(
                button(
                    _('edit'),
                    url_for('profile_settings', category='modules')))
        tabs['display'].buttons.append(
            button(_('edit'), url_for('profile_settings', category='display')))
    return render_template(
        'tabs.html',
        tabs=tabs,
        title=_('profile'),
        crumbs=[_('profile')])


@app.route('/profile/settings/<category>', methods=['POST', 'GET'])
@login_required
def profile_settings(category: str) -> Union[str, Response]:
    form = getattr(
        importlib.import_module('openatlas.forms.setting'),
        f"{uc_first(category)}Form")()
    if form.validate_on_submit():
        settings = {}
        for field in form:
            if field.type in ['CSRFTokenField', 'HiddenField', 'SubmitField']:
                continue
            if field.name == 'name':
                current_user.real_name = field.data
            elif field.name == 'email':
                current_user.email = field.data
            else:
                value = field.data
                if field.type == 'BooleanField':
                    value = 'True' if value else ''
                settings[field.name] = value
        Transaction.begin()
        try:
            current_user.update()
            current_user.update_settings(settings)
            Transaction.commit()
            session['language'] = current_user.settings['language']
            flash(_('info update'), 'info')
        except Exception as e:  # pragma: no cover
            Transaction.rollback()
            g.logger.log('error', 'database', 'transaction failed', e)
            flash(_('error transaction'), 'error')
        return redirect(f"{url_for('profile_index')}#tab-{category}")
    set_form_settings(form, True)
    return render_template(
        'content.html',
        content=display_form(form, manual_page='profile'),
        title=_('profile'),
        crumbs=[
            [_('profile'), f"{url_for('profile_index')}#tab-{category}"],
            _(category)])


@app.route('/profile/password', methods=['POST', 'GET'])
@login_required
def profile_password() -> Union[str, Response]:
    form = PasswordForm()
    if form.validate_on_submit():
        current_user.password = bcrypt.hashpw(
            form.password.data.encode('utf-8'),
            bcrypt.gensalt()).decode('utf-8')
        current_user.update()
        flash(_('info password updated'), 'info')
        return redirect(url_for('profile_index'))
    return render_template(
        'user/password.html',
        form=form,
        title=_('profile'),
        crumbs=[
            [_('profile'), url_for('profile_index')],
            _('change password')])
