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

    def test_create_node_group_template(self):
        url = self.URL + '/node-group-templates'
        self.responses.post(url, status_code=202,
                            json={'node_group_template': self.body})

        resp = self.client.node_group_templates.create(**self.body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(self.body,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, ng.NodeGroupTemplate)
        self.assertFields(self.body, resp)

    def test_node_group_template_list(self):
        url = self.URL + '/node-group-templates'
        self.responses.get(url, json={'node_group_templates': [self.body]})

        resp = self.client.node_group_templates.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], ng.NodeGroupTemplate)
        self.assertFields(self.body, resp[0])

    def test_node_group_template_get(self):
        url = self.URL + '/node-group-templates/id'
        self.responses.get(url, json={'node_group_template': self.body})
        resp = self.client.node_group_templates.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, ng.NodeGroupTemplate)
        self.assertFields(self.body, resp)

    def test_node_group_template_delete(self):
        url = self.URL + '/node-group-templates/id'
        self.responses.delete(url, status_code=204)

        self.client.node_group_templates.delete('id')

        self.assertEqual(url, self.responses.last_request.url)
