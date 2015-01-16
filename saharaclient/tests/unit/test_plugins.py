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

from saharaclient.api import plugins
from saharaclient.tests.unit import base


class PluginTest(base.BaseTestCase):
    body = {
        'description': 'description',
        'name': 'name',
        'version': '1'
    }

    def test_plugins_list(self):
        url = self.URL + '/plugins'
        self.responses.get(url, json={'plugins': [self.body]})

        resp = self.client.plugins.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], plugins.Plugin)
        self.assertFields(self.body, resp[0])

    def test_plugins_get(self):
        url = self.URL + '/plugins/name'
        self.responses.get(url, json={'plugin': self.body})

        resp = self.client.plugins.get('name')
        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, plugins.Plugin)
        self.assertFields(self.body, resp)

    def test_plugins_get_version_details(self):
        url = self.URL + '/plugins/name/1'
        self.responses.get(url, json={'plugin': self.body})

        resp = self.client.plugins.get_version_details('name', '1')
        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, plugins.Plugin)
        self.assertFields(self.body, resp)

    def test_convert_to_cluster_template(self):
        url = self.URL + '/plugins/plugin/1/convert-config/template'
        response = {
            'name': 'name',
            'description': 'description',
            'plugin_name': 'plugin',
            'hadoop_version': '1',
        }
        self.responses.post(url, status_code=202,
                            json={'cluster_template': response})

        resp = self.client.plugins.convert_to_cluster_template(
            'plugin', 1, 'template', 'file')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(response, resp)
