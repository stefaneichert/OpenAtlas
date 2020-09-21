from flask import url_for, g

from openatlas import app
from openatlas.models.entity import Entity
from openatlas.models.node import Node
from tests.base import TestBaseCase


class ApiTests(TestBaseCase):

    def test_api(self) -> None:
        with app.app_context():  # type: ignore
            rv = self.app.post(url_for('place_insert'),
                               data={'name': 'Nostromos',
                                     'description': 'In space, no one can hears you scream',
                                     'alias-0': 'Valhöll'})
            place_id = rv.location.split('/')[-1]
            with app.test_request_context():
                app.preprocess_request()  # type: ignore
                event = Entity.insert('E8', 'Event Horizon')
                event.link('P7', Entity.get_by_id(place_id))
                place_node = Node.get_hierarchy('Place')
                place = Entity.get_by_id(place_id)
                place.link("P2", place_node)
                reference = Entity.insert('E31', 'https://openatlas.eu', 'external reference')
                source = Entity.insert('E33', 'Necronomicon')
                unit_node = Node.get_hierarchy('Administrative Unit')
                unit_sub1 = g.nodes[unit_node.subs[0]]
                unit_sub2 = g.nodes[unit_node.subs[1]]

            # Data for geometric results
            data = {'name': 'Asgard', 'alias-0': 'Valhöll', 'geonames_id': '123',
                    'geonames_precision': True, 'geonames_description': "Muhahahaa",
                    'description': 'In space, no one can hears you scream',
                    unit_node.id: str([unit_sub1.id, unit_sub2.id]),
                    'gis_points': """[{
                            "type":"Feature",
                            "geometry":{"type":"Point","coordinates":[9,17]},
                            "properties":{"name":"Valhalla","description":"","shapeType":"centerpoint"}}]""",
                    'gis_lines': """[{
                            "type":"Feature",
                            "geometry":{
                                "type":"LineString",
                                "coordinates":[[9.75307425847859,17.8111792731339],
                                [9.75315472474904,17.8110005175436],[9.75333711496205,17.8110873417098]]},
                            "properties":{"name":"","description":"","shapeType":"line"}}]""",
                    'gis_polygons': """[{
                            "type":"Feature",
                            "geometry":{
                                "type":"Polygon",
                                "coordinates":[[[9.75307425847859,17.8111792731339],
                                [9.75315472474904,17.8110005175436],[9.75333711496205,17.8110873417098],
                                [9.75307425847859,17.8111792731339]]]},
                            "properties":{"name":"","description":"","shapeType":"shape"}}]"""}
            rv = self.app.post(url_for('place_insert', origin_id=reference.id), data=data,
                               follow_redirects=True)
            assert b'Asgard' in rv.data
            rv = self.app.post(url_for('place_insert', origin_id=source.id), data=data,
                               follow_redirects=True)
            assert b'Asgard' in rv.data
            rv = self.app.post(url_for('place_insert', origin_id=source.id), data=data,
                               follow_redirects=True)
            assert b'Necronomicon' in rv.data

            # API Tests
            rv = self.app.get(url_for('api_index'))
            assert b'Test API' in rv.data
            rv = self.app.get(url_for('api_get_latest', limit=10))
            assert b'Nostromos' in rv.data
            rv = self.app.get(url_for('api_entity', id_=place_id))
            assert b'Nostromos' in rv.data
            rv = self.app.get(url_for('api_download_entity', id_=place_id))
            assert b'@context"' in rv.data
            rv = self.app.get(url_for('api_get_by_menu_item', code='reference'))
            assert b'openatlas' in rv.data
            rv = self.app.get(url_for('api_get_by_class', class_code='E33'))
            assert b'Necronomicon' in rv.data
            rv = self.app.get(url_for('api_get_by_class', class_code='E31'))
            assert b'https://openatlas.eu' in rv.data

            # Parameter: filter and first
            rv = self.app.get(
                url_for('api_get_by_menu_item', code='place', limit=10, sort='desc', column='name',
                        filter='or(eq,name,Nostromos)', first=place_id))
            assert b'Nostromos' in rv.data
            rv = self.app.get(url_for('api_get_by_menu_item', code='reference'))
            assert b'openatlas' in rv.data

            # Parameter: last
            rv = self.app.get(url_for('api_get_by_class', class_code='E18', last=place_id))
            assert b'entities' in rv.data

            # Parameter: filter
            rv = self.app.get(url_for('api_get_by_class', class_code='E18',
                                      filter='AND(in,name,[Nostromos:hallo])'))
            assert b'Nostromos' in rv.data
            rv = self.app.get(url_for('api_get_by_class', class_code='E18',
                                      filter='AND(in,name,[Nostromos])'))
            assert b'Nostromos' in rv.data
            rv = self.app.get(url_for('api_get_by_class', class_code='E18',
                                      filter='or(like,name,Nostr)'))
            assert b'Nostromos' in rv.data

            # Parameter: show
            rv = self.app.get(url_for('api_get_by_class', class_code='E33', show='types'))
            assert b'Necronomicon' in rv.data
            rv = self.app.get(url_for('api_get_by_class', class_code='E33', show='none'))
            assert b'Necronomicon' in rv.data

            # Parameter: count
            rv = self.app.get(url_for('api_get_by_class', class_code='E33', count='none'))
            assert b'1' in rv.data
            rv = self.app.get(url_for('api_get_by_menu_item', code='reference', count='none'))
            assert b'2' in rv.data  # Assert can vary, to get around use \n

            # Error Codes
            rv = self.app.get(url_for('api_entity', id_=99999999))
            assert b'404a' in rv.data
            rv = self.app.get(url_for('api_get_by_class', class_code='E18', last=1231223121321))
            assert b'404a' in rv.data
            rv = self.app.get(url_for('api_entity', id_="EEEE"))
            assert b'404b' in rv.data
            rv = self.app.get(url_for('api_get_latest', limit=99999))
            assert b'404e' in rv.data
            rv = self.app.get(url_for('api_get_by_class', class_code='E19'))
            assert b'404' in rv.data
            rv = self.app.get(url_for('api_get_by_menu_item', code='TWART'))
            assert b'404c' in rv.data
            # rv = self.app.post(url_for('api_get_entities_by_json'))
            # assert b'405' in rv.data
            self.app.get(url_for('logout'), follow_redirects=True)
            rv = self.app.get(url_for('api_entity', id_=place_id))
            assert b'403' in rv.data
