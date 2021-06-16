from typing import Any, Dict, List, Optional

from openatlas.models.entity import Entity
from openatlas.models.gis import Gis
from openatlas.models.link import Link


class Geojson:

    @staticmethod
    def get_geojson(entities: List[Entity]) -> List[Dict[str, Any]]:
        geoms = None
        out = []
        for entity in entities:
            if entity.class_.view == 'place' or entity.class_.name in ['find', 'artifact']:
                geoms = Gis.get_by_id(Link.get_linked_entity(entity.id, 'P53').id)
            elif entity.class_.name == 'object_location':
                geoms = Gis.get_by_id(entity.id)
            if geoms:
                for geom in geoms:
                    out.append(Geojson.get_entity(entity, geom))
            out.append(Geojson.get_entity(entity))
        return out

    @staticmethod
    def get_entity(entity: Entity, geom: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        features = {
            'type': 'Feature',
            'geometry': geom,
            'properties': {
                '@id': entity.id,
                'systemClass': entity.class_.name,
                'name': entity.name,
                'description': entity.description,
                'begin_earliest': entity.begin_from,
                'begin_latest': entity.begin_to,
                'begin_comment': entity.begin_comment,
                'end_earliest': entity.end_from,
                'end_latest': entity.end_to,
                'end_comment': entity.end_comment,
                'types': Geojson.get_node(entity)
            }}
        return features

    @staticmethod
    def get_node(entity: Entity) -> Optional[List[Dict[str, Any]]]:
        nodes = []
        for node in entity.nodes:
            out = [node.name]
            nodes.append(': '.join(out))
        return nodes if nodes else None

    @staticmethod
    def return_output(output: List[Any]) -> Dict[str, Any]:
        return {'type': 'FeatureCollection', 'features': output}
