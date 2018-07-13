# Copyright (c) 2015 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import mock
from osc_lib.tests import utils as osc_utils

from saharaclient.api import cluster_templates as api_ct
from saharaclient.api import clusters as api_cl
from saharaclient.api import images as api_img
from saharaclient.api import node_group_templates as api_ngt
from saharaclient.osc.v2 import clusters as osc_cl
from saharaclient.tests.unit.osc.v1 import test_clusters as tc_v1

CLUSTER_INFO = {
    "description": "Cluster template for tests",

    "use_autoconfig": True,
    "is_default": False,
    "node_groups": [
        {
            "count": 2,
            "id": "ng_id",
            "name": "fakeng",
            "plugin_name": 'fake',
            "plugin_version": '0.1',
            "node_group_template_id": 'ngt_id'
        }
    ],
    "plugin_version": "0.1",
    "is_public": False,
    "plugin_name": "fake",
    "id": "cluster_id",
    "anti_affinity": [],
    "name": "fake",
    "is_protected": False,
    "cluster_template_id": "ct_id",
    "neutron_management_network": "net_id",
    "user_keypair_id": "test",
    "status": 'Active',
    "default_image_id": "img_id",
    'verification': {
        'status': 'GREEN',
        'id': 'ver_id',
        'cluster_id': 'cluster_id',
        'checks': [
            {
                'status': 'GREEN',
                'name': 'Some check'
            }
        ]
    }
}

CT_INFO = {
    "plugin_name": "fake",
    "plugin_version": "0.1",
    "name": '"template',
    "id": "ct_id"
}

NGT_INFO = {
    'id': 'ngt_id',
    'name': 'fakeng'
}


class TestClusters(tc_v1.TestClusters):
    def setUp(self):
        super(TestClusters, self).setUp()
        self.app.api_version['data_processing'] = '2'
        self.cl_mock = (
            self.app.client_manager.data_processing.clusters)
        self.ngt_mock = (
            self.app.client_manager.data_processing.node_group_templates)
        self.ct_mock = (
            self.app.client_manager.data_processing.cluster_templates)
        self.img_mock = (
            self.app.client_manager.data_processing.images)
        self.cl_mock.reset_mock()
        self.ngt_mock.reset_mock()
        self.ct_mock.reset_mock()
        self.img_mock.reset_mock()


class TestCreateCluster(TestClusters):
    # TODO(apavlov): check for creation with --json
    def setUp(self):
        super(TestCreateCluster, self).setUp()
        self.cl_mock.create.return_value = api_cl.Cluster(
            None, CLUSTER_INFO)
        self.cl_mock.find_unique.return_value = api_cl.Cluster(
            None, CLUSTER_INFO)
        self.ct_mock.find_unique.return_value = api_ct.ClusterTemplate(
            None, CT_INFO)
        self.img_mock.find_unique.return_value = api_img.Image(
            None, {'id': 'img_id'})
        self.net_mock = self.app.client_manager.network
        self.net_mock.find_network.return_value = mock.Mock(id='net_id')
        self.net_mock.reset_mock()

        # Command to test
        self.cmd = osc_cl.CreateCluster(self.app, None)

    def test_cluster_create_minimum_options(self):
        arglist = ['--name', 'fake', '--cluster-template', 'template',
                   '--image', 'ubuntu']
        verifylist = [('name', 'fake'), ('cluster_template', 'template'),
                      ('image', 'ubuntu')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.create.assert_called_once_with(
            cluster_template_id='ct_id', count=None, default_image_id='img_id',
            description=None, plugin_version='0.1', is_protected=False,
            is_public=False, is_transient=False, name='fake', net_id=None,
            plugin_name='fake', user_keypair_id=None)

    def test_cluster_create_all_options(self):
        arglist = ['--name', 'fake', '--cluster-template', 'template',
                   '--image', 'ubuntu', '--user-keypair', 'test',
                   '--neutron-network', 'net', '--description', 'descr',
                   '--transient', '--public', '--protected']

        verifylist = [('name', 'fake'), ('cluster_template', 'template'),
                      ('image', 'ubuntu'), ('user_keypair', 'test'),
                      ('neutron_network', 'net'), ('description', 'descr'),
                      ('transient', True), ('public', True),
                      ('protected', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.create.assert_called_once_with(
            cluster_template_id='ct_id', count=None, default_image_id='img_id',
            description='descr', plugin_version='0.1', is_protected=True,
            is_public=True, is_transient=True, name='fake', net_id='net_id',
            plugin_name='fake', user_keypair_id='test')

        # Check that columns are correct
        expected_columns = ('Anti affinity', 'Cluster template id',
                            'Description', 'Id', 'Image',
                            'Is protected', 'Is public', 'Name',
                            'Neutron management network', 'Node groups',
                            'Plugin name', 'Plugin version', 'Status',
                            'Use autoconfig', 'User keypair id')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('', 'ct_id', 'Cluster template for tests',
                         'cluster_id', 'img_id', False, False, 'fake',
                         'net_id', 'fakeng:2', 'fake', '0.1', 'Active', True,
                         'test')
        self.assertEqual(expected_data, data)

    def test_cluster_create_with_count(self):
        clusters_mock = mock.Mock()
        clusters_mock.to_dict.return_value = {
            'clusters': [{'cluster': {'id': 'cluster1_id'}},
                         {'cluster': {'id': 'cluster2_id'}}]
        }
        self.cl_mock.create.return_value = clusters_mock

        arglist = ['--name', 'fake', '--cluster-template', 'template',
                   '--image', 'ubuntu', '--count', '2']
        verifylist = [('name', 'fake'), ('cluster_template', 'template'),
                      ('image', 'ubuntu'), ('count', 2)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.create.assert_called_once_with(
            cluster_template_id='ct_id', count=2, default_image_id='img_id',
            description=None, plugin_version='0.1', is_protected=False,
            is_public=False, is_transient=False, name='fake', net_id=None,
            plugin_name='fake', user_keypair_id=None)

        # Check that columns are correct
        expected_columns = ('fake',)
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('cluster_id',)
        self.assertEqual(expected_data, data)


class TestListClusters(TestClusters):
    def setUp(self):
        super(TestListClusters, self).setUp()
        self.cl_mock.list.return_value = [api_cl.Cluster(
            None, CLUSTER_INFO)]

        # Command to test
        self.cmd = osc_cl.ListClusters(self.app, None)

    def test_clusters_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Plugin name', 'Plugin version',
                            'Status']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('fake', 'cluster_id', 'fake', '0.1', 'Active')]
        self.assertEqual(expected_data, list(data))

    def test_clusters_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Plugin name', 'Plugin version',
                            'Status', 'Description', 'Image']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('fake', 'cluster_id', 'fake', '0.1', 'Active',
                          'Cluster template for tests', 'img_id')]
        self.assertEqual(expected_data, list(data))

    def test_clusters_list_extra_search_opts(self):
        arglist = ['--plugin', 'fake', '--plugin-version', '0.1', '--name',
                   'fake']
        verifylist = [('plugin', 'fake'), ('plugin_version', '0.1'),
                      ('name', 'fake')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Plugin name', 'Plugin version',
                            'Status']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('fake', 'cluster_id', 'fake', '0.1', 'Active')]
        self.assertEqual(expected_data, list(data))


class TestShowCluster(TestClusters):
    def setUp(self):
        super(TestShowCluster, self).setUp()
        self.cl_mock.find_unique.return_value = api_cl.Cluster(
            None, CLUSTER_INFO)

        # Command to test
        self.cmd = osc_cl.ShowCluster(self.app, None)

    def test_cluster_show(self):
        arglist = ['fake']
        verifylist = [('cluster', 'fake')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.find_unique.assert_called_once_with(name='fake')

        # Check that columns are correct
        expected_columns = ('Anti affinity', 'Cluster template id',
                            'Description', 'Id', 'Image',
                            'Is protected', 'Is public', 'Name',
                            'Neutron management network', 'Node groups',
                            'Plugin name', 'Plugin version', 'Status',
                            'Use autoconfig', 'User keypair id')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('', 'ct_id', 'Cluster template for tests',
                         'cluster_id', 'img_id', False, False, 'fake',
                         'net_id', 'fakeng:2', 'fake', '0.1', 'Active', True,
                         'test')
        self.assertEqual(expected_data, data)

    def test_cluster_show_verification(self):
        arglist = ['fake', '--verification']
        verifylist = [('cluster', 'fake'), ('verification', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.find_unique.assert_called_once_with(name='fake')

        # Check that columns are correct
        expected_columns = ('Anti affinity', 'Cluster template id',
                            'Description', 'Health check (some check)', 'Id',
                            'Image', 'Is protected', 'Is public', 'Name',
                            'Neutron management network', 'Node groups',
                            'Plugin name', 'Plugin version', 'Status',
                            'Use autoconfig', 'User keypair id',
                            'Verification status')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('', 'ct_id', 'Cluster template for tests', 'GREEN',
                         'cluster_id', 'img_id', False, False, 'fake',
                         'net_id', 'fakeng:2', 'fake', '0.1', 'Active', True,
                         'test', 'GREEN')
        self.assertEqual(expected_data, data)


class TestDeleteCluster(TestClusters):
    def setUp(self):
        super(TestDeleteCluster, self).setUp()
        self.cl_mock.find_unique.return_value = api_cl.Cluster(
            None, CLUSTER_INFO)

        # Command to test
        self.cmd = osc_cl.DeleteCluster(self.app, None)

    def test_cluster_delete(self):
        arglist = ['fake']
        verifylist = [('cluster', ['fake'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.delete.assert_called_once_with('cluster_id')


class TestUpdateCluster(TestClusters):
    def setUp(self):
        super(TestUpdateCluster, self).setUp()
        self.cl_mock.update.return_value = mock.Mock(
            cluster=CLUSTER_INFO.copy())
        self.cl_mock.find_unique.return_value = api_cl.Cluster(
            None, CLUSTER_INFO)

        # Command to test
        self.cmd = osc_cl.UpdateCluster(self.app, None)

    def test_cluster_update_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_cluster_update_nothing_updated(self):
        arglist = ['fake']

        verifylist = [('cluster', 'fake')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.update.assert_called_once_with('cluster_id')

    def test_cluster_update_all_options(self):
        arglist = ['fake', '--name', 'fake', '--description', 'descr',
                   '--public', '--protected']

        verifylist = [('cluster', 'fake'), ('name', 'fake'),
                      ('description', 'descr'), ('is_public', True),
                      ('is_protected', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.update.assert_called_once_with(
            'cluster_id', description='descr', is_protected=True,
            is_public=True, name='fake')

        # Check that columns are correct
        expected_columns = ('Anti affinity', 'Cluster template id',
                            'Description', 'Id', 'Image',
                            'Is protected', 'Is public', 'Name',
                            'Neutron management network', 'Node groups',
                            'Plugin name', 'Plugin version', 'Status',
                            'Use autoconfig', 'User keypair id')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('', 'ct_id', 'Cluster template for tests',
                         'cluster_id', 'img_id', False, False, 'fake',
                         'net_id', 'fakeng:2', 'fake', '0.1', 'Active', True,
                         'test')
        self.assertEqual(expected_data, data)

    def test_cluster_update_private_unprotected(self):
        arglist = ['fake', '--private', '--unprotected']

        verifylist = [('cluster', 'fake'), ('is_public', False),
                      ('is_protected', False)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.update.assert_called_once_with(
            'cluster_id', is_protected=False, is_public=False)


class TestScaleCluster(TestClusters):
    def setUp(self):
        super(TestScaleCluster, self).setUp()
        self.cl_mock.scale.return_value = mock.Mock(
            cluster=CLUSTER_INFO.copy())
        self.cl_mock.find_unique.return_value = api_cl.Cluster(
            None, CLUSTER_INFO)

        # Command to test
        self.cmd = osc_cl.ScaleCluster(self.app, None)

    def test_cluster_scale_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_cluster_scale_resize(self):
        self.ngt_mock.find_unique.return_value = api_ngt.NodeGroupTemplate(
            None, NGT_INFO)
        arglist = ['fake', '--instances', 'fakeng:1']

        verifylist = [('cluster', 'fake'),
                      ('instances', ['fakeng:1'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.scale.assert_called_once_with(
            'cluster_id',
            {'resize_node_groups': [
                {'count': 1,
                 'name': 'fakeng'}]}
        )

        # Check that columns are correct
        expected_columns = ('Anti affinity', 'Cluster template id',
                            'Description', 'Id', 'Image',
                            'Is protected', 'Is public', 'Name',
                            'Neutron management network', 'Node groups',
                            'Plugin name', 'Plugin version', 'Status',
                            'Use autoconfig', 'User keypair id')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('', 'ct_id', 'Cluster template for tests',
                         'cluster_id', 'img_id', False, False, 'fake',
                         'net_id', 'fakeng:2', 'fake', '0.1', 'Active', True,
                         'test')
        self.assertEqual(expected_data, data)

    def test_cluster_scale_add_ng(self):
        new_ng = {'name': 'new', 'id': 'new_id'}
        self.ngt_mock.find_unique.return_value = api_ngt.NodeGroupTemplate(
            None, new_ng)
        arglist = ['fake', '--instances', 'new:1']

        verifylist = [('cluster', 'fake'), ('instances', ['new:1'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.scale.assert_called_once_with(
            'cluster_id',
            {'add_node_groups': [
                {'count': 1,
                 'node_group_template_id': 'new_id',
                 'name': 'new'}
            ]})


class TestVerificationUpdateCluster(TestClusters):
    def setUp(self):
        super(TestVerificationUpdateCluster, self).setUp()
        self.cl_mock.find_unique.return_value = api_cl.Cluster(
            None, CLUSTER_INFO)
        self.cl_mock.verification_update.return_value = api_cl.Cluster(
            None, CLUSTER_INFO)

        # Command to test
        self.cmd = osc_cl.VerificationUpdateCluster(self.app, None)

    def test_verification_show(self):
        arglist = ['fake', '--show']
        verifylist = [('cluster', 'fake'), ('show', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.find_unique.assert_called_once_with(name='fake')

        # Check that columns are correct
        expected_columns = ('Health check (some check)', 'Verification status')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('GREEN', 'GREEN')
        self.assertEqual(expected_data, data)

    def test_verification_start(self):
        arglist = ['fake', '--start']
        verifylist = [('cluster', 'fake'), ('status', 'START')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.cl_mock.verification_update.assert_called_once_with(
            'cluster_id', 'START')
