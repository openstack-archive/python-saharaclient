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

from saharaclient.api import plugins
from saharaclient.tests.unit import base


class PluginTest(base.BaseTestCase):
    body = {
        'description': 'description',
        'name': 'name',
        'version': '1'
    }

    @mock.patch('requests.get')
    def test_plugins_list(self, mget):
        mget.return_value = base.FakeResponse(200, [self.body], 'plugins')

        resp = self.client.plugins.list()
        self.assertEqual('http://localhost:8386/plugins',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], plugins.Plugin)
        self.assertFields(self.body, resp[0])

    @mock.patch('requests.get')
    def test_plugins_get(self, mget):
        mget.return_value = base.FakeResponse(200, self.body, 'plugin')

        resp = self.client.plugins.get('name')
        self.assertEqual('http://localhost:8386/plugins/name',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, plugins.Plugin)
        self.assertFields(self.body, resp)

    @mock.patch('requests.get')
    def test_plugins_get_version_details(self, mget):
        mget.return_value = base.FakeResponse(200, self.body, 'plugin')

        resp = self.client.plugins.get_version_details('name', '1')
        self.assertEqual('http://localhost:8386/plugins/name/1',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, plugins.Plugin)
        self.assertFields(self.body, resp)

    @mock.patch('requests.post')
    def test_convert_to_cluster_template(self, mpost):
        response = {
            'name': 'name',
            'description': 'description',
            'plugin_name': 'plugin',
            'hadoop_version': '1',
        }
        mpost.return_value = base.FakeResponse(202, response,
                                               'cluster_template')

        resp = self.client.plugins.convert_to_cluster_template(
            'plugin', 1, 'template', 'file')

        self.assertEqual(
            'http://localhost:8386/plugins/plugin/1/convert-config/template',
            mpost.call_args[0][0])
        self.assertEqual(response, resp)
