import os
from typing import Any, Dict, List, Optional, Union

from flask import flash, g, render_template, session, url_for
from flask_babel import lazy_gettext as _
from flask_wtf import FlaskForm
from werkzeug.exceptions import abort
from werkzeug.utils import redirect, secure_filename
from werkzeug.wrappers import Response

from openatlas import app, logger
from openatlas.database.connect import Transaction
from openatlas.forms.form import build_form
from openatlas.forms.util import (
    populate_insert_form, populate_update_form, process_form_data)
from openatlas.models.entity import Entity
from openatlas.models.gis import Gis, InvalidGeomException
from openatlas.models.link import Link
from openatlas.models.overlay import Overlay
from openatlas.models.place import get_structure
from openatlas.models.reference_system import ReferenceSystem
from openatlas.models.type import Type
from openatlas.util.image_processing import ImageProcessing
from openatlas.util.util import (
    is_authorized, link, required_group, was_modified)


@app.route('/insert/<class_>', methods=['POST', 'GET'])
@app.route('/insert/<class_>/<int:origin_id>', methods=['POST', 'GET'])
@required_group('contributor')
def insert(
        class_: str,
        origin_id: Optional[int] = None) -> Union[str, Response]:
    check_insert_access(class_)
    origin = Entity.get_by_id(origin_id) if origin_id else None
    form = build_form(class_, origin=origin)
    if form.validate_on_submit():
        return redirect(save(form, class_=class_, origin=origin))
    populate_insert_form(form, class_, origin)
    place_info = get_place_info_for_insert(g.classes[class_].view, origin)
    return render_template(
        'entity/insert.html',
        form=form,
        view_name=g.classes[class_].view,
        gis_data=place_info['gis_data'],
        geonames_module=check_geonames_module(class_),
        writable=os.access(app.config['UPLOAD_DIR'], os.W_OK),
        overlays=place_info['overlays'],
        title=_(g.classes[class_].view),
        crumbs=add_crumbs(
            class_,
            origin,
            place_info['structure'],
            insert_=True))


@app.route('/update/<int:id_>', methods=['POST', 'GET'])
@required_group('contributor')
def update(id_: int) -> Union[str, Response]:
    entity = Entity.get_by_id(id_, types=True, aliases=True)
    check_update_access(entity)
    place_info = get_place_info_for_update(entity)
    form = build_form(
        entity.class_.name,
        entity,
        location=place_info['location'])
    if form.validate_on_submit():
        if isinstance(entity, Type) and not check_type(entity, form):
            return redirect(url_for('view', id_=entity.id))
        if was_modified(form, entity):  # pragma: no cover
            del form.save
            flash(_('error modified'), 'error')
            return render_template(
                'entity/update.html',
                form=form,
                entity=entity,
                modifier=link(logger.get_log_info(entity.id)['modifier']))
        return redirect(save(form, entity))
    populate_update_form(form, entity)
    if entity.class_.view in ['artifact', 'place']:
        entity.set_image_for_places()
    return render_template(
        'entity/update.html',
        form=form,
        entity=entity,
        gis_data=place_info['gis_data'],
        overlays=place_info['overlays'],
        geonames_module=check_geonames_module(entity.class_.name),
        title=entity.name,
        crumbs=add_crumbs(
            class_=entity.class_.name,
            origin=entity,
            structure=place_info['structure']))


def check_type(entity: Type, form: FlaskForm) -> bool:
    valid = True
    root = g.types[entity.root[0]]
    new_super_id = getattr(form, str(root.id)).data
    new_super = g.types[int(new_super_id)] if new_super_id else None
    if new_super:
        if new_super.id == entity.id:
            flash(_('error type self as super'), 'error')
            valid = False
        if new_super.root and entity.id in new_super.root:
            flash(_('error type sub as super'), 'error')
            valid = False
    return valid


def get_place_info_for_update(entity: Entity) -> Dict[str, Any]:
    if entity.class_.view not in ['artifact', 'place']:
        return {
            'structure': None,
            'gis_data': None,
            'overlays': None,
            'location': None}
    structure = get_structure(entity)
    return {
        'structure': structure,
        'gis_data': Gis.get_all([entity], structure),
        'overlays': Overlay.get_by_object(entity),
        'location': entity.get_linked_entity_safe('P53', types=True)}


def get_place_info_for_insert(
        class_view: str,
        origin: Optional[Entity]) -> Dict[str, Any]:
    if class_view not in ['artifact', 'place']:
        return {'structure': None, 'gis_data': None, 'overlays': None}
    structure = get_structure(super_=origin)
    return {
        'structure': structure,
        'gis_data': Gis.get_all([origin] if origin else None, structure),
        'overlays': Overlay.get_by_object(origin)
        if origin and origin.class_.view == 'place' else None}


def check_geonames_module(class_: str) -> bool:
    return class_ == 'place' and ReferenceSystem.get_by_name('GeoNames').classes


def check_update_access(entity: Entity) -> None:
    check_insert_access(entity.class_.name)
    if isinstance(entity, Type) and (
            entity.category == 'system'
            or entity.category == 'standard' and not entity.root):
        abort(403)


def check_insert_access(class_: str) -> None:
    if class_ not in g.classes \
            or not g.classes[class_].view \
            or not is_authorized(g.classes[class_].write_access):
        abort(403)  # pragma: no cover


def add_crumbs(
        class_: str,
        origin: Union[Entity, None],
        structure: Optional[Dict[str, Any]],
        insert_: Optional[bool] = False) -> List[Any]:
    view = g.classes[class_].view
    label = origin.class_.name if origin else view
    if label in g.class_view_mapping:
        label = g.class_view_mapping[label]
    label = _(label.replace('_', ' '))
    crumbs = [
        [label, url_for('index', view=origin.class_.view if origin else view)],
        link(origin)]
    if structure:
        crumbs = [
            [_('place'), url_for('index', view='place')],
            structure['place']
            if origin and origin.class_.name != 'place' else '',
            structure['feature'],
            structure['stratigraphic_unit'],
            link(origin)]
    if view == 'type':
        crumbs = [[_('types'), url_for('type_index')]]
        if isinstance(origin, Type) and origin.root:
            for type_id in origin.root:
                crumbs += [link(g.types[type_id])]
        crumbs += [origin]
    sibling_count = 0
    if origin \
            and origin.class_.name == 'stratigraphic_unit' \
            and structure \
            and insert_:
        for item in structure['siblings']:
            if item.class_.name == class_:  # pragma: no cover
                sibling_count += 1
    siblings = f" ({sibling_count} {_('exists')})" if sibling_count else ''
    return crumbs + \
        [f'+ {g.classes[class_].label}{siblings}' if insert_ else _('edit')]


def insert_file(
        form: FlaskForm,
        origin: Optional[Entity] = None) -> Union[str, Response]:
    filenames = []
    url = url_for('index', view=g.classes['file'].view)
    try:
        Transaction.begin()
        entity_name = form.name.data.strip()
        for count, file in enumerate(form.file.data):
            entity = Entity.insert('file', file.filename)
            url = link_and_get_redirect_url(form, entity, 'file', origin)
            # Add 'a' to prevent emtpy temporary filename, has no side effects
            filename = secure_filename(f'a{file.filename}')
            new_name = f"{entity.id}.{filename.rsplit('.', 1)[1].lower()}"
            file.save(str(app.config['UPLOAD_DIR'] / new_name))
            filenames.append(new_name)
            if session['settings']['image_processing']:
                ImageProcessing.resize_image(new_name)
            if len(form.file.data) > 1:
                form.name.data = f'{entity_name}_{str(count + 1).zfill(2)}'
                if origin:
                    url = f"{url_for('view', id_=origin.id)}#tab-file"
            entity.update(form)
            update_links(entity, form, 'insert', origin)
            logger.log_user(entity.id, 'insert')
        Transaction.commit()
        flash(_('entity created'), 'info')
    except Exception as e:  # pragma: no cover
        Transaction.rollback()
        for filename in filenames:
            (app.config['UPLOAD_DIR'] / filename).unlink()
        logger.log('error', 'database', 'transaction failed', e)
        flash(_('error transaction'), 'error')
        url = url_for('index', view=g.classes['file'].view)
    return url


def save(
        form: FlaskForm,
        entity: Optional[Entity] = None,
        class_: Optional[str] = None,
        origin: Optional[Entity] = None) -> Union[str, Response]:
    if class_ == 'file' and not entity:
        return insert_file(form, origin)
    Transaction.begin()
    action = 'update'
    try:
        if not entity:
            action = 'insert'
            entity = insert_entity(form, class_)
        if isinstance(entity, ReferenceSystem):
            entity.name = entity.name \
                if hasattr(entity, 'system') and entity.system \
                else form.name.data
            entity.description = form.description.data
            entity.website_url = form.website_url.data \
                if form.website_url.data else None
            entity.resolver_url = form.resolver_url.data \
                if form.resolver_url.data else None
            entity.placeholder = form.placeholder.data \
                if form.placeholder.data else None
            entity.update_system(form)
            if hasattr(form, 'classes'):
                entity.add_classes(form)
        else:
            entity.update(process_form_data(form, entity, origin))
            class_ = entity.class_.name
        update_links(entity, form, action, origin)
        url = link_and_get_redirect_url(form, entity, class_, origin)
        logger.log_user(entity.id, action)
        Transaction.commit()
        flash(
            _('entity created') if action == 'insert' else _('info update'),
            'info')
    except InvalidGeomException as e:  # pragma: no cover
        Transaction.rollback()
        logger.log(
            'error',
            'database',
            'transaction failed because of invalid geom',
            e)
        flash(_('Invalid geom entered'), 'error')
        if action == 'update' and entity:
            url = url_for(
                'update',
                id_=entity.id,
                origin_id=origin.id if origin else None)
        else:
            url = url_for('index', view=g.classes[class_].view)
    except Exception as e:  # pragma: no cover
        Transaction.rollback()
        logger.log('error', 'database', 'transaction failed', e)
        flash(_('error transaction'), 'error')
        if action == 'update' and entity:
            url = url_for(
                'update',
                id_=entity.id,
                origin_id=origin.id if origin else None)
        else:
            url = url_for('index', view=g.classes[class_].view)
            if class_ in ['administrative_unit', 'type']:
                url = url_for('type_index')
    return url


def insert_entity(form: FlaskForm, class_: str) \
        -> Union[Entity, Type, ReferenceSystem]:
    if class_ == 'reference_system':
        return ReferenceSystem.insert_system(form)
    entity = Entity.insert(class_, form.name.data)
    if class_ == 'artifact' or g.classes[class_].view == 'place':
        entity.link(
            'P53',
            Entity.insert('object_location', f'Location of {form.name.data}'))
    return entity


def update_links(
        entity: Entity,
        form: FlaskForm,
        action: str,
        origin: Union[Entity, None]) -> None:
    if entity.class_.reference_systems:
        ReferenceSystem.update_links(form, entity)
    if entity.class_.view == 'actor':
        if action == 'update':
            entity.delete_links(['P74', 'OA8', 'OA9'])
        if form.residence.data:
            object_ = Entity.get_by_id(form.residence.data)
            entity.link('P74', object_.get_linked_entity_safe('P53'))
        if form.begins_in.data:
            object_ = Entity.get_by_id(form.begins_in.data)
            entity.link('OA8', object_.get_linked_entity_safe('P53'))
        if form.ends_in.data:
            object_ = Entity.get_by_id(form.ends_in.data)
            entity.link('OA9', object_.get_linked_entity_safe('P53'))
    if entity.class_.view == 'event':
        if action == 'update':
            entity.delete_links(
                ['P7', 'P24', 'P25', 'P26', 'P27', 'P108', 'P117'])
        entity.link_string('P117', form.event.data)
        if hasattr(form, 'place') and form.place.data:
            entity.link(
                'P7',
                Link.get_linked_entity_safe(int(form.place.data), 'P53'))
        if entity.class_.name == 'acquisition':
            entity.link_string('P24', form.given_place.data)
        if entity.class_.name == 'move':
            entity.link_string('P25', form.artifact.data)  # Moved objects
            entity.link_string('P25', form.person.data)  # Moved persons
            if form.place_from.data:  # Link place for move from
                linked_place = Link.get_linked_entity_safe(
                    int(form.place_from.data),
                    'P53')
                entity.link('P27', linked_place)
            if form.place_to.data:  # Link place for move to
                entity.link(
                    'P26',
                    Link.get_linked_entity_safe(int(form.place_to.data), 'P53'))
        elif entity.class_.name == 'production':
            entity.link_string('P108', form.artifact.data)
    elif entity.class_.view in ['artifact', 'place']:
        location = entity.get_linked_entity_safe('P53')
        if action == 'update':
            Gis.delete_by_entity(location)
        location.update(form)
        Gis.insert(location, form)
        if entity.class_.name == 'artifact':
            entity.delete_links(['P52'])
            entity.link_string('P52', form.actor.data)
    elif entity.class_.view == 'source' and not origin:
        if action == 'update':
            entity.delete_links(['P128'], inverse=True)
        entity.link_string('P128', form.artifact.data, inverse=True)


def link_and_get_redirect_url(
        form: FlaskForm,
        entity: Entity,
        class_: str,
        origin: Union[Entity, None] = None) -> str:
    url = url_for('view', id_=entity.id)
    if origin and class_ not in ('administrative_unit', 'type'):
        url = f"{url_for('view', id_=origin.id)}#tab-{entity.class_.view}"
        if origin.class_.view == 'reference':
            if entity.class_.name == 'file':
                origin.link('P67', entity, form.page.data)
            else:
                link_id = origin.link('P67', entity)[0]
                url = url_for(
                    'reference_link_update',
                    link_id=link_id,
                    origin_id=origin.id)
        elif entity.class_.name == 'file':
            entity.link('P67', origin)
            url = f"{url_for('view', id_=origin.id)}#tab-file"
        elif entity.class_.view == 'reference':
            link_id = entity.link('P67', origin)[0]
            url = url_for(
                'reference_link_update',
                link_id=link_id,
                origin_id=origin.id)
        elif origin.class_.view in ['place', 'feature', 'stratigraphic_unit']:
            if entity.class_.view == 'place' \
                    or entity.class_.name == 'artifact':
                origin.link('P46', entity)
                url = url_for('view', id_=entity.id)
        elif origin.class_.view in ['source', 'file']:
            origin.link('P67', entity)
        elif entity.class_.view == 'source':
            entity.link('P67', origin)
        elif origin.class_.view == 'event':  # Involvement from actor
            link_id = origin.link('P11', entity)[0]
            url = url_for(
                'involvement_update',
                id_=link_id,
                origin_id=origin.id)
        elif origin.class_.view == 'actor' and entity.class_.view == 'event':
            link_id = entity.link('P11', origin)[0]  # Involvement from event
            url = url_for(
                'involvement_update',
                id_=link_id,
                origin_id=origin.id)
        elif origin.class_.view == 'actor' and entity.class_.view == 'actor':
            link_id = origin.link('OA7', entity)[0]  # Actor with actor relation
            url = url_for('relation_update', id_=link_id, origin_id=origin.id)

    if hasattr(form, 'continue_') and form.continue_.data == 'yes':
        url = url_for(
            'insert',
            class_=class_,
            origin_id=origin.id if origin else None)
        if class_ in ('administrative_unit', 'type'):
            root_id = origin.root[0] \
                if isinstance(origin, Type) and origin.root else origin.id
            super_id = getattr(form, str(root_id)).data
            url = url_for(
                'insert',
                class_=class_,
                origin_id=str(super_id) if super_id else root_id)
    elif hasattr(form, 'continue_') \
            and form.continue_.data in ['sub', 'human_remains']:
        class_ = form.continue_.data
        if class_ == 'sub':
            if entity.class_.name == 'place':
                class_ = 'feature'
            elif entity.class_.name == 'feature':
                class_ = 'stratigraphic_unit'
            elif entity.class_.name == 'stratigraphic_unit':
                class_ = 'artifact'
        url = url_for('insert', class_=class_, origin_id=entity.id)
    return url
