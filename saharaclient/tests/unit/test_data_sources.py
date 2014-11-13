# Copyright (c) 2014 Mirantis Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from saharaclient.api import data_sources as ds
from saharaclient.tests.unit import base

import json


class DataSourceTest(base.BaseTestCase):
    body = {
        'name': 'name',
        'url': 'url',
        'description': 'descr',
        'data_source_type': 'hdfs',
        'credential_user': 'user',
        'credential_pass': '123'
    }

    response = {
        'name': 'name',
        'url': 'url',
        'description': 'descr',
        'type': 'hdfs',
        'credentials': {
            'user': 'user',
            'password': '123'
        }
    }

    @mock.patch('requests.post')
    def test_create_data_sources(self, mpost):
        mpost.return_value = base.FakeResponse(202, self.response,
                                               'data_source')

        resp = self.client.data_sources.create(**self.body)

        self.assertEqual('http://localhost:8386/data-sources',
                         mpost.call_args[0][0])
        self.assertEqual(self.response, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, ds.DataSources)
        self.assertFields(self.response, resp)

    @mock.patch('requests.get')
    def test_data_sources_list(self, mget):
        mget.return_value = base.FakeResponse(200, [self.response],
                                              'data_sources')

        resp = self.client.data_sources.list()

        self.assertEqual('http://localhost:8386/data-sources',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], ds.DataSources)
        self.assertFields(self.response, resp[0])

    @mock.patch('requests.get')
    def test_data_sources_get(self, mget):
        mget.return_value = base.FakeResponse(200, self.response,
                                              'data_source')

        resp = self.client.data_sources.get('id')

        self.assertEqual('http://localhost:8386/data-sources/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, ds.DataSources)
        self.assertFields(self.response, resp)

    @mock.patch('requests.delete')
    def test_data_sources_delete(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.data_sources.delete('id')

        self.assertEqual('http://localhost:8386/data-sources/id',
                         mdelete.call_args[0][0])
