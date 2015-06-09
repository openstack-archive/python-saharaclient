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

    update_json = {
        'name': 'UpdatedName',
        'url': 'hdfs://myfakeserver/fakepath'
    }

    def test_create_data_sources(self):
        url = self.URL + '/data-sources'
        self.responses.post(url, status_code=202,
                            json={'data_source': self.response})

        resp = self.client.data_sources.create(**self.body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(self.response,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, ds.DataSources)
        self.assertFields(self.response, resp)

    def test_data_sources_list(self):
        url = self.URL + '/data-sources'
        self.responses.get(url, json={'data_sources': [self.response]})

        resp = self.client.data_sources.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], ds.DataSources)
        self.assertFields(self.response, resp[0])

    def test_data_sources_get(self):
        url = self.URL + '/data-sources/id'
        self.responses.get(url, json={'data_source': self.response})

        resp = self.client.data_sources.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, ds.DataSources)
        self.assertFields(self.response, resp)

    def test_data_sources_delete(self):
        url = self.URL + '/data-sources/id'
        self.responses.delete(url, status_code=204)

        self.client.data_sources.delete('id')

        self.assertEqual(url, self.responses.last_request.url)

    def test_update_data_sources(self):
        update_url = self.URL + '/data-sources/id'
        self.responses.put(update_url, status_code=202,
                           json=self.update_json)
        updated = self.client.data_sources.update("id", self.update_json)
        self.assertEqual(self.update_json["name"], updated.name)
        self.assertEqual(self.update_json["url"], updated.url)
