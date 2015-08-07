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
        },
        "use_autoconfig": False,
    }

    update_json = {
        "cluster_template": {
            'name': 'UpdatedName',
            'description': 'Updated description',
            'plugin_name': 'plugin',
            'hadoop_version': '1',
            'node_groups': {
                'name': 'master-node',
                'flavor_id': '3',
                'node_processes': ['namenode', 'datanode'],
                'count': 1
            },
            "use_autoconfig": True,
        }
    }

    def test_create_cluster_template(self):
        url = self.URL + '/cluster-templates'
        self.responses.post(url, status_code=202,
                            json={'cluster_template': self.body})

        resp = self.client.cluster_templates.create(**self.body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(self.body,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, ct.ClusterTemplate)
        self.assertFields(self.body, resp)

    def test_cluster_template_list(self):
        url = self.URL + '/cluster-templates'
        self.responses.get(url, json={'cluster_templates': [self.body]})

        resp = self.client.cluster_templates.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], ct.ClusterTemplate)
        self.assertFields(self.body, resp[0])

    def test_cluster_template_get(self):
        url = self.URL + '/cluster-templates/id'
        self.responses.get(url, json={'cluster_template': self.body})

        resp = self.client.cluster_templates.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, ct.ClusterTemplate)
        self.assertFields(self.body, resp)

    def test_cluster_template_delete(self):
        url = self.URL + '/cluster-templates/id'
        self.responses.delete(url, status_code=204)

        self.client.cluster_templates.delete('id')

        self.assertEqual(url, self.responses.last_request.url)

    def test_cluster_template_update(self):
        url = self.URL + '/cluster-templates'
        self.responses.post(url, status_code=202,
                            json={'cluster_template': self.body})
        resp = self.client.cluster_templates.create(**self.body)

        update_url = self.URL + '/cluster-templates/id'
        self.responses.put(update_url, status_code=202, json=self.update_json)

        updated = self.client.cluster_templates.update(
            "id",
            resp.name,
            resp.plugin_name,
            resp.hadoop_version,
            description=getattr(resp, "description", None),
            cluster_configs=getattr(resp, "cluster_configs", None),
            node_groups=getattr(resp, "node_groups", None),
            anti_affinity=getattr(resp, "anti_affinity", None),
            net_id=getattr(resp, "neutron_management_network", None),
            default_image_id=getattr(resp, "default_image_id", None),
            use_autoconfig=True,
        )

        self.assertIsInstance(updated, ct.ClusterTemplate)
        self.assertFields(self.update_json["cluster_template"], updated)
