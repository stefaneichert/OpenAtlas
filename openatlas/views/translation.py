# Copyright 2017 by Alexander Watzinger and others. Please see README.md for licensing information
from flask import render_template, url_for, flash, request
from flask_babel import lazy_gettext as _
from flask_wtf import Form
from werkzeug.utils import redirect
from wtforms import StringField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import InputRequired

import openatlas
from openatlas import app
from openatlas.forms import build_custom_form
from openatlas.models.entity import EntityMapper
from openatlas.util.util import uc_first, link, truncate_string, required_group, append_node_data, \
    print_base_type


class TranslationForm(Form):
    name = StringField(uc_first(_('name')), validators=[InputRequired()])
    description = TextAreaField(uc_first(_('content')))
    save = SubmitField(_('insert'))
    insert_and_continue = SubmitField(_('insert and continue'))
    continue_ = HiddenField()


@app.route('/translation/insert/<int:source_id>', methods=['POST', 'GET'])
@required_group('editor')
def translation_insert(source_id):
    source = EntityMapper.get_by_id(source_id)
    form = build_custom_form(TranslationForm, 'Source translation')
    return render_template('translation/insert.html', source=source, form=form)


@app.route('/translation/view/<int:id_>')
@required_group('readonly')
def translation_view(id_):
    translation = EntityMapper.get_by_id(id_)
    source = translation.get_linked_entity('P73', True)
    data = {'info': []}
    append_node_data(data['info'], translation)
    return render_template(
        'translation/view.html',
        translation=translation,
        source=source,
        data=data)


@app.route('/translation/delete/<int:id_>')
@required_group('editor')
def translation_delete(id_):
    openatlas.get_cursor().execute('BEGIN')
    EntityMapper.delete(id_)
    openatlas.get_cursor().execute('COMMIT')
    flash(_('entity deleted'), 'info')
    return redirect(url_for('source_index'))


@app.route('/translation/update/<int:id_>', methods=['POST', 'GET'])
@required_group('editor')
def translation_update(id_):
    translation = EntityMapper.get_by_id(id_)
    return render_template('translation/update.html', translation=translation)
