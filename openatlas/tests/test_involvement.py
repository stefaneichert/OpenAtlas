from flask import url_for

from openatlas import app
from openatlas.models.entity import EntityMapper
from openatlas.models.link import LinkMapper
from openatlas.models.node import NodeMapper
from openatlas.test_base import TestBaseCase


class InvolvementTests(TestBaseCase):

    def test_involvement(self):
        with app.app_context():
            self.login()
            rv = self.app.post(url_for('event_insert', code='E8'),
                               data={
                                    'name': 'Event Horizon',
                                    'date_begin_year': '1949',
                                    'date_begin_month': '10',
                                    'date_begin_day': '8',
                                    'date_end_year': '1951'})
            event_id = int(rv.location.split('/')[-1])
            with app.test_request_context():
                app.preprocess_request()
                actor_id = EntityMapper.insert('E21', 'Captain Miller').id
                involvement_id = NodeMapper.get_hierarchy_by_name('Involvement').id

            # Add involvement
            rv = self.app.get(url_for('involvement_insert', origin_id=actor_id))
            assert b'Involvement' in rv.data
            data = {
                'event': '[' + str(event_id) + ']',
                'activity': 'P11',
                involvement_id: involvement_id}
            rv = self.app.post(
                url_for('involvement_insert', origin_id=actor_id), data=data, follow_redirects=True)
            assert b'Event Horizon' in rv.data
            data = {'actor': '[' + str(actor_id) + ']', 'continue_': 'yes', 'activity': 'P22'}
            rv = self.app.post(
                url_for('involvement_insert', origin_id=event_id), data=data, follow_redirects=True)
            assert b'Event Horizon' in rv.data
            self.app.get(url_for('event_view', id_=event_id))

            # Update involvement
            with app.test_request_context():
                app.preprocess_request()
                link_id = LinkMapper.get_links(event_id, 'P22')[0].id
            rv = self.app.get(url_for('involvement_update', id_=link_id, origin_id=event_id))
            assert b'Captain' in rv.data
            rv = self.app.post(
                url_for('involvement_update', id_=link_id, origin_id=actor_id),
                data={'description': 'Infinite Space - Infinite Terror', 'activity': 'P23'},
                follow_redirects=True)
            assert b'Infinite Space - Infinite Terror' in rv.data
            self.app.get(url_for('event_view', id_=event_id))
