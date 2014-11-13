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

from saharaclient.api import cluster_templates as ct
from saharaclient.tests.unit import base

import json


class ClusterTemplateTest(base.BaseTestCase):
    body = {
        'name': 'name',
        'description': 'description',
        'plugin_name': 'plugin',
        'hadoop_version': '1',
        'node_groups': {
            'name': 'master-node',
            'flavor_id': '2',
            'node_processes': ['namenode'],
            'count': 1
        }
    }

    @mock.patch('requests.post')
    def test_create_cluster_template(self, mpost):
        mpost.return_value = base.FakeResponse(
            202, self.body, 'cluster_template')

        resp = self.client.cluster_templates.create(**self.body)

        self.assertEqual('http://localhost:8386/cluster-templates',
                         mpost.call_args[0][0])
        self.assertEqual(self.body, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, ct.ClusterTemplate)
        self.assertFields(self.body, resp)

    @mock.patch('requests.get')
    def test_cluster_template_list(self, mget):
        mget.return_value = base.FakeResponse(
            200, [self.body], 'cluster_templates')

        resp = self.client.cluster_templates.list()

        self.assertEqual('http://localhost:8386/cluster-templates',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], ct.ClusterTemplate)
        self.assertFields(self.body, resp[0])

    @mock.patch('requests.get')
    def test_cluster_template_get(self, mget):
        mget.return_value = base.FakeResponse(
            200, self.body, 'cluster_template')

        resp = self.client.cluster_templates.get('id')

        self.assertEqual('http://localhost:8386/cluster-templates/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, ct.ClusterTemplate)
        self.assertFields(self.body, resp)

    @mock.patch('requests.delete')
    def test_cluster_template_delete(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.cluster_templates.delete('id')

        self.assertEqual('http://localhost:8386/cluster-templates/id',
                         mdelete.call_args[0][0])
