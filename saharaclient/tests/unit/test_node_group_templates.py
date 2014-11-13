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

from saharaclient.api import node_group_templates as ng
from saharaclient.tests.unit import base

import json


class NodeGroupTemplateTest(base.BaseTestCase):
    body = {
        "name": "name",
        "plugin_name": "plugin",
        "hadoop_version": "1",
        "flavor_id": "2",
        "description": "description",
        "volumes_per_node": "3",
        "volumes_size": "4",
        "node_processes": ["datanode"]
    }

    @mock.patch('requests.post')
    def test_create_node_group_template(self, mpost):
        mpost.return_value = base.FakeResponse(202, self.body,
                                               'node_group_template')

        resp = self.client.node_group_templates.create(**self.body)

        self.assertEqual('http://localhost:8386/node-group-templates',
                         mpost.call_args[0][0])
        self.assertEqual(self.body, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, ng.NodeGroupTemplate)
        self.assertFields(self.body, resp)

    @mock.patch('requests.get')
    def test_node_group_template_list(self, mget):
        mget.return_value = base.FakeResponse(200, [self.body],
                                              'node_group_templates')

        resp = self.client.node_group_templates.list()

        self.assertEqual('http://localhost:8386/node-group-templates',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], ng.NodeGroupTemplate)
        self.assertFields(self.body, resp[0])

    @mock.patch('requests.get')
    def test_node_group_template_get(self, mget):
        mget.return_value = base.FakeResponse(200, self.body,
                                              'node_group_template')

        resp = self.client.node_group_templates.get('id')

        self.assertEqual('http://localhost:8386/node-group-templates/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, ng.NodeGroupTemplate)
        self.assertFields(self.body, resp)

    @mock.patch('requests.delete')
    def test_node_group_template_delete(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.node_group_templates.delete('id')

        self.assertEqual('http://localhost:8386/node-group-templates/id',
                         mdelete.call_args[0][0])
