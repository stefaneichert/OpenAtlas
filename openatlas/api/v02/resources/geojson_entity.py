import ast
from typing import Any, Dict, List, Optional, Union

from flask import g, url_for

from openatlas import app
from openatlas.api.v02.resources.error import EntityDoesNotExistError
from openatlas.models.entity import Entity
from openatlas.models.link import Link
from openatlas.util.display import get_file_path


class GeoJsonEntity:

    @staticmethod
    def get_links(entity: Entity) -> Optional[List[Dict[str, str]]]:
        links = []
        for link in Link.get_links(entity.id):
            links.append({'label': link.range.name,
                          'relationTo': url_for('entity', id_=link.range.id, _external=True),
                          'relationType': 'crm:' + link.property.code + '_'
                                          + link.property.i18n['en'].replace(' ', '_')})
        for link in Link.get_links(entity.id, inverse=True):
            links.append({'label': link.domain.name,
                          'relationTo': url_for('entity', id_=link.domain.id, _external=True),
                          'relationType': 'crm:' + link.property.code + 'i_'
                                          + link.property.i18n['en'].replace(' ', '_')})
        return links if links else None

    @staticmethod
    def get_file(entity: Entity) -> Optional[List[Dict[str, str]]]:
        files = []
        for link in Link.get_links(entity.id, codes="P67", inverse=True):
            if link.domain.class_.name == 'file':
                path = get_file_path(link.domain.id)
                files.append({'@id': url_for('entity', id_=link.domain.id, _external=True),
                              'title': link.domain.name,
                              'license': GeoJsonEntity.get_license(link.domain.id),
                              'url': url_for('display_file_api',
                                             filename=path.name,
                                             _external=True) if path else "N/A"})
        return files if files else None

    @staticmethod
    def get_license(entity_id: int) -> str:
        file_license = ""
        for link in Link.get_links(entity_id):
            if link.property.code == "P2":
                file_license = link.range.name
        return file_license

    @staticmethod
    def get_node(entity: Entity) -> Optional[List[Dict[str, Any]]]:
        nodes = []
        for node in entity.nodes:
            nodes_dict = {'identifier': url_for('entity', id_=node.id, _external=True),
                          'label': node.name}
            for link in Link.get_links(entity.id):
                if link.range.id == node.id and link.description:
                    nodes_dict['value'] = link.description
                    if link.range.id == node.id and node.description:
                        nodes_dict['unit'] = node.description
            ##### If errors occure with value types, then add this line. Otherwise, delete it.
            # if 'unit' not in nodes_dict and node.description:
            #     nodes_dict['description'] = node.description

            hierarchy = []
            for root in node.root:
                hierarchy.append(g.nodes[root].name)
            hierarchy.reverse()
            nodes_dict['hierarchy'] = ' > '.join(map(str, hierarchy))
            nodes.append(nodes_dict)
        return nodes if nodes else None

    @staticmethod
    def get_time(entity: Entity) -> Optional[Dict[str, Any]]:
        time = {}
        start = {'earliest': entity.begin_from, 'latest': entity.begin_to,
                 'comment': entity.begin_comment}
        time['start'] = start
        end = {'earliest': entity.end_from, 'latest': entity.end_to, 'comment': entity.end_comment}
        time['end'] = end
        return time if time else None

    @staticmethod
    # Todo: API coverage, remove no cover below
    def get_geom_by_entity(entity: Entity) -> Union[str, Dict[str, Any]]:  # pragma: nocover
        if entity.class_.code != 'E53':  # pragma: nocover
            return 'Wrong class'
        geom = []
        for shape in ['point', 'polygon', 'linestring']:
            sql = """
                     SELECT
                         {shape}.id,
                         {shape}.name,
                         {shape}.description,
                         public.ST_AsGeoJSON({shape}.geom) AS geojson
                     FROM model.entity e
                     JOIN gis.{shape} {shape} ON e.id = {shape}.entity_id
                     WHERE e.id = %(entity_id)s;""".format(shape=shape)
            g.execute(sql, {'entity_id': entity.id})
            for row in g.cursor.fetchall():
                meta = ast.literal_eval(row.geojson)
                meta['title'] = row.name.replace('"', '\"') if row.name else ''
                meta['description'] = row.description.replace('"',
                                                              '\"') if row.description else ''
                geom.append(meta)
        if len(geom) == 1:
            return geom[0]
        else:
            return {'type': 'GeometryCollection', 'geometries': geom}

    @staticmethod
    def get_reference_systems(entity: Entity) -> List[Dict[str, Union[str, Any]]]:
        ref = []
        for link in Link.get_links(entity.id, codes="P67", inverse=True):
            if link.domain.class_.code == 'E32':
                system = g.reference_systems[link.domain.id]
                ref.append({'identifier': (system.resolver_url if system.resolver_url else '')
                                          + link.description,
                            'type': g.nodes[link.type.id].name,
                            'reference_system': system.name})
        return ref if ref else None

    @staticmethod
    def get_entity_by_id(id_: int) -> Entity:
        try:
            entity = Entity.get_by_id(id_, nodes=True, aliases=True)
        # Todo: get_by_id return an abort if id does not exist... I don't get to the exception
        except EntityDoesNotExistError:  # pragma: nocover
            raise EntityDoesNotExistError
        return entity

    @staticmethod
    def get_entity(entity: Entity, parser: Dict[str, Any]) -> Dict[str, Any]:
        type_ = 'FeatureCollection'

        class_code = ''.join(entity.class_.code + " " + entity.class_.i18n['en']).replace(" ", "_")
        features = {'@id': url_for('entity_view', id_=entity.id, _external=True),
                    'type': 'Feature',
                    'crmClass': "crm:" + class_code,
                    'properties': {'title': entity.name}}

        # Descriptions
        if entity.description:
            features['description'] = [{'value': entity.description}]

        # Alias
        if entity.aliases and 'names' in parser['show']:
            features['names'] = []
            for key, value in entity.aliases.items():
                features['names'].append({"alias": value})

        # Relations
        features['relations'] = GeoJsonEntity.get_links(entity) if 'relations' in parser[
            'show'] else None

        # Types
        features['types'] = GeoJsonEntity.get_node(entity) if 'types' in parser['show'] else None

        # Depictions
        features['depictions'] = GeoJsonEntity.get_file(entity) if 'depictions' in parser[
            'show'] else None

        # Time spans
        features['when'] = {'timespans': [GeoJsonEntity.get_time(entity)]} if 'when' in parser[
            'show'] else None

        features['links'] = GeoJsonEntity.get_reference_systems(entity) if 'links' in parser[
            'show'] else None

        # Geometry
        if 'geometry' in parser['show'] and entity.class_.code == 'E53':
            features['geometry'] = GeoJsonEntity.get_geom_by_entity(entity)
        elif 'geometry' in parser['show'] and entity.class_.code == 'E18':
            features['geometry'] = GeoJsonEntity.get_geom_by_entity(
                Link.get_linked_entity(entity.id, 'P53'))

        data: Dict[str, Any] = {'type': type_,
                                '@context': app.config['API_SCHEMA'],
                                'features': [features]}
        return data
