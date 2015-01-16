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

from saharaclient.api import clusters as cl
from saharaclient.tests.unit import base

import json


class ClusterTest(base.BaseTestCase):
    body = {
        'name': 'name',
        'plugin_name': 'fake',
        'hadoop_version': '0.1',
        'cluster_template_id': 'id',
    }

    def test_create_cluster_with_template(self,):
        url = self.URL + '/clusters'
        self.responses.post(url, status_code=202, json={'cluster': self.body})

        resp = self.client.clusters.create(**self.body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(self.body,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, cl.Cluster)
        self.assertFields(self.body, resp)

    def test_create_cluster_without_template(self):
        body = self.body.copy()
        del body['cluster_template_id']
        body.update({'default_image_id': 'image_id', 'cluster_configs': {},
                     'node_groups': ['ng1', 'ng2']})

        url = self.URL + '/clusters'
        self.responses.post(url, status_code=202, json={'cluster': body})

        resp = self.client.clusters.create(**body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(body, json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, cl.Cluster)
        self.assertFields(body, resp)

    def test_clusters_list(self):
        url = self.URL + '/clusters'
        self.responses.get(url, json={'clusters': [self.body]})

        resp = self.client.clusters.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], cl.Cluster)
        self.assertFields(self.body, resp[0])

    def test_clusters_get(self):
        url = self.URL + '/clusters/id'
        self.responses.get(url, json={'cluster': self.body})

        resp = self.client.clusters.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, cl.Cluster)
        self.assertFields(self.body, resp)

    def test_clusters_scale(self):
        url = self.URL + '/clusters/id'
        self.responses.put(url, status_code=202, json=self.body)

        scale_body = {
            'resize_node_groups': [
                {
                    'count': 2,
                    'name': 'name1'
                },
            ],
            'add_node_groups': [
                {
                    'count': 1,
                    'name': 'name2',
                    'node_group_template_id': 'id'
                }
            ]
        }

        resp = self.client.clusters.scale('id', scale_body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(scale_body,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, cl.Cluster)
        self.assertFields(self.body, resp)

    def test_clusters_delete(self):
        url = self.URL + '/clusters/id'
        self.responses.delete(url, status_code=204)

        self.client.clusters.delete('id')

        self.assertEqual(url, self.responses.last_request.url)
