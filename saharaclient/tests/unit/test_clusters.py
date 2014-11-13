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

    @mock.patch('requests.post')
    def test_create_cluster_with_template(self, mpost):
        mpost.return_value = base.FakeResponse(
            202, self.body, 'cluster')

        resp = self.client.clusters.create(**self.body)

        self.assertEqual('http://localhost:8386/clusters',
                         mpost.call_args[0][0])
        self.assertEqual(self.body, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, cl.Cluster)
        self.assertFields(self.body, resp)

    @mock.patch('requests.post')
    def test_create_cluster_without_template(self, mpost):
        body = self.body.copy()
        del body['cluster_template_id']
        body.update({'default_image_id': 'image_id', 'cluster_configs': {},
                     'node_groups': ['ng1', 'ng2']})
        mpost.return_value = base.FakeResponse(
            202, body, 'cluster')

        resp = self.client.clusters.create(**body)

        self.assertEqual('http://localhost:8386/clusters',
                         mpost.call_args[0][0])
        self.assertEqual(body, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, cl.Cluster)
        self.assertFields(body, resp)

    @mock.patch('requests.get')
    def test_clusters_list(self, mget):
        mget.return_value = base.FakeResponse(
            200, [self.body], 'clusters')

        resp = self.client.clusters.list()

        self.assertEqual('http://localhost:8386/clusters',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], cl.Cluster)
        self.assertFields(self.body, resp[0])

    @mock.patch('requests.get')
    def test_clusters_get(self, mget):
        mget.return_value = base.FakeResponse(
            200, self.body, 'cluster')

        resp = self.client.clusters.get('id')

        self.assertEqual('http://localhost:8386/clusters/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, cl.Cluster)
        self.assertFields(self.body, resp)

    @mock.patch('requests.put')
    def test_clusters_scale(self, mput):
        mput.return_value = base.FakeResponse(202, self.body)

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

        self.assertEqual('http://localhost:8386/clusters/id',
                         mput.call_args[0][0])
        self.assertEqual(scale_body, json.loads(mput.call_args[0][1]))
        self.assertIsInstance(resp, cl.Cluster)
        self.assertFields(self.body, resp)

    @mock.patch('requests.delete')
    def test_clusters_delete(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.clusters.delete('id')

        self.assertEqual('http://localhost:8386/clusters/id',
                         mdelete.call_args[0][0])
