import subprocess
from pathlib import Path
from subprocess import call, run
from typing import Any, Union

from flask import g, render_template, request, send_from_directory, url_for
from flask_babel import lazy_gettext as _
from werkzeug.utils import redirect
from werkzeug.wrappers import Response

from openatlas import app
from openatlas.display.util import required_group, get_file_path
from openatlas.forms.form import get_table_form
from openatlas.models.entity import Entity


@app.route('/download/<path:filename>')
@required_group('readonly')
def download_file(filename: str) -> Any:
    return send_from_directory(
        app.config['UPLOAD_DIR'],
        filename,
        as_attachment=True)


@app.route('/display/<path:filename>')
@required_group('readonly')
def display_file(filename: str) -> Any:
    if request.args.get('size'):
        return send_from_directory(
            app.config['RESIZED_IMAGES'] / request.args.get('size'),
            filename)
    return send_from_directory(app.config['UPLOAD_DIR'], filename)


@app.route('/display_logo/<path:filename>')
def display_logo(filename: str) -> Any:
    return send_from_directory(app.config['UPLOAD_DIR'], filename)


@app.route('/file/set_profile_image/<int:id_>/<int:origin_id>')
def set_profile_image(id_: int, origin_id: int) -> Response:
    Entity.set_profile_image(id_, origin_id)
    return redirect(url_for('view', id_=origin_id))


@app.route('/file/remove_profile_image/<int:entity_id>')
def file_remove_profile_image(entity_id: int) -> Response:
    entity = Entity.get_by_id(entity_id)
    entity.remove_profile_image()
    return redirect(url_for('view', id_=entity.id))


@app.route('/file/add/<int:id_>/<view>', methods=['GET', 'POST'])
@required_group('contributor')
def file_add(id_: int, view: str) -> Union[str, Response]:
    entity = Entity.get_by_id(id_)
    if request.method == 'POST':
        if request.form['checkbox_values']:
            entity.link_string('P67', request.form['checkbox_values'])
        return redirect(f"{url_for('view', id_=entity.id)}#tab-{view}")
    return render_template(
        'content.html',
        content=get_table_form(
            g.view_class_mapping[view],
            entity.get_linked_entities('P67')),
        title=entity.name,
        crumbs=[
            [_(entity.class_.view), url_for('index', view=entity.class_.view)],
            entity,
            f"{_('link')} {_(view)}"])


@app.route('/file/iiif/<int:id_>', methods=['GET', 'POST'])
@required_group('contributor')
def make_iiif_available(id_: int):

    command =f"convert {get_file_path(id_)} -define tiff:tile-geometry=256x256 -compress jpeg 'ptif:{Path(app.config['IIIF_DIR']) / str(id_)}'"
    # call_ = call(f"convert {get_file_path(id_)} "
    #     f"-define tiff:tile-geometry=256x256 -compress jpeg "
    #     f"'ptif:{app.config['IIIF_DIR'] / str(id_)}'", shell=True)
    subprocess.Popen(        command, shell=True)
    return redirect(url_for('view', id_=id_))
