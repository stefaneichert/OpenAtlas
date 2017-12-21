# Copyright 2017 by Alexander Watzinger and others. Please see README.md for licensing information
from flask import url_for

from openatlas import app, EntityMapper
from openatlas.test_base import TestBaseCase


class ReferenceTest(TestBaseCase):

    def test_reference(self):
        self.login()
        with app.app_context():

            # reference insert
            rv = self.app.get(url_for('reference_insert', code='bibliography'))
            assert b'+ Bibliography' in rv.data
            rv = self.app.get(url_for('reference_insert', code='edition'))
            assert b'+ Edition' in rv.data
            rv = self.app.get(url_for('reference_insert', code='carrier'))
            assert b'+ Carrier' in rv.data
            form_data = {'name': 'Test reference', 'description': 'Reference description'}
            rv = self.app.post(url_for('reference_insert', code='bibliography'), data=form_data)
            bibliography_id = rv.location.split('/')[-1]
            form_data['continue_'] = 'yes'
            rv = self.app.post(
                url_for('reference_insert', code='carrier'), data=form_data, follow_redirects=True)
            assert b'An entry has been created' in rv.data
            rv = self.app.get(url_for('reference_index'))

            # reference update
            assert b'Test reference' in rv.data
            rv = self.app.get(url_for('reference_update', id_=bibliography_id))
            assert b'Test reference' in rv.data
            form_data['name'] = 'Test reference updated'
            rv = self.app.post(
                url_for('reference_update', id_=bibliography_id),
                data=form_data,
                follow_redirects=True)
            assert b'Test reference updated' in rv.data

            # reference link
            batman = EntityMapper.insert('E21', 'Batman')
            rv = self.app.get(url_for('reference_add', origin_id=batman.id))
            assert b'Batman' in rv.data
            rv = self.app.post(
                url_for('reference_add', origin_id=batman.id),
                data={'reference': bibliography_id},
                follow_redirects=True)
            assert b'Test reference updated' in rv.data

            rv = self.app.get(
                url_for('reference_add2', reference_id=bibliography_id, class_name='actor'))
            assert b'Batman' in rv.data
            rv = self.app.post(
                url_for('reference_add2', reference_id=bibliography_id, class_name='actor'),
                data={'actor': batman.id},
                follow_redirects=True)
            assert b'Test reference updated' in rv.data

            rv = self.app.get(url_for('reference_view', id_=bibliography_id, unlink_id=batman.id))
            assert b'removed'in rv.data

            # reference delete
            rv = self.app.get(
                url_for('reference_delete', id_=bibliography_id), follow_redirects=True)
            assert b'The entry has been deleted.' in rv.data
