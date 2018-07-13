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

from osc_lib.tests import utils as osc_utils

from saharaclient.api import cluster_templates as api_ct
from saharaclient.api import node_group_templates as api_ngt
from saharaclient.osc.v2 import cluster_templates as osc_ct
from saharaclient.tests.unit.osc.v1 import test_cluster_templates as tct_v1

CT_INFO = {
    "description": "Cluster template for tests",
    "use_autoconfig": True,
    "is_default": False,
    "node_groups": [
        {
            "count": 2,
            "id": "d29631fc-0fad-434b-80aa-7a3e9526f57c",
            "name": "fakeng",
            "plugin_name": 'fake',
            "plugin_version": '0.1'
        }
    ],
    "plugin_version": "0.1",
    "is_public": False,
    "plugin_name": "fake",
    "id": "0647061f-ab98-4c89-84e0-30738ea55750",
    "anti_affinity": [],
    "name": "template",
    "is_protected": False,
    "domain_name": 'domain.org.'
}


class TestClusterTemplates(tct_v1.TestClusterTemplates):
    def setUp(self):
        super(TestClusterTemplates, self).setUp()
        self.app.api_version['data_processing'] = '2'
        self.ct_mock = (
            self.app.client_manager.data_processing.cluster_templates)
        self.ngt_mock = (
            self.app.client_manager.data_processing.node_group_templates)
        self.ct_mock.reset_mock()
        self.ngt_mock.reset_mock()


class TestCreateClusterTemplate(TestClusterTemplates):
    # TODO(apavlov): check for creation with --json
    def setUp(self):
        super(TestCreateClusterTemplate, self).setUp()
        self.ct_mock.create.return_value = api_ct.ClusterTemplate(
            None, CT_INFO)
        self.ngt_mock.find_unique.return_value = api_ngt.NodeGroupTemplate(
            None, CT_INFO['node_groups'][0])

        # Command to test
        self.cmd = osc_ct.CreateClusterTemplate(self.app, None)

    def test_ct_create_minimum_options(self):
        arglist = ['--name', 'template', '--node-groups', 'fakeng:2']
        verifylist = [('name', 'template'),
                      ('node_groups', ['fakeng:2'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ct_mock.create.assert_called_once_with(
            description=None, plugin_version='0.1', is_protected=False,
            is_public=False, name='template', node_groups=[
                {'count': 2, 'name': 'fakeng',
                 'node_group_template_id':
                     'd29631fc-0fad-434b-80aa-7a3e9526f57c'}],
            plugin_name='fake', use_autoconfig=False, shares=None,
            cluster_configs=None, domain_name=None)

    def test_ct_create_all_options(self):
        arglist = ['--name', 'template', '--node-groups', 'fakeng:2',
                   '--anti-affinity', 'datanode',
                   '--description', 'descr',
                   '--autoconfig', '--public', '--protected',
                   '--domain-name', 'domain.org.']

        verifylist = [('name', 'template'),
                      ('node_groups', ['fakeng:2']),
                      ('description', 'descr'), ('autoconfig', True),
                      ('public', True), ('protected', True),
                      ('domain_name', 'domain.org.')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ct_mock.create.assert_called_once_with(
            description='descr', plugin_version='0.1', is_protected=True,
            is_public=True, name='template', node_groups=[
                {'count': 2, 'name': 'fakeng',
                 'node_group_template_id':
                     'd29631fc-0fad-434b-80aa-7a3e9526f57c'}],
            plugin_name='fake', use_autoconfig=True, shares=None,
            cluster_configs=None, domain_name='domain.org.')

        # Check that columns are correct
        expected_columns = ('Anti affinity', 'Description',
                            'Domain name', 'Id', 'Is default',
                            'Is protected', 'Is public', 'Name', 'Node groups',
                            'Plugin name', 'Plugin version', 'Use autoconfig')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('', 'Cluster template for tests', 'domain.org.',
                         '0647061f-ab98-4c89-84e0-30738ea55750', False, False,
                         False, 'template', 'fakeng:2', 'fake', '0.1', True)
        self.assertEqual(expected_data, data)


class TestListClusterTemplates(TestClusterTemplates):
    def setUp(self):
        super(TestListClusterTemplates, self).setUp()
        self.ct_mock.list.return_value = [api_ct.ClusterTemplate(
            None, CT_INFO)]

        # Command to test
        self.cmd = osc_ct.ListClusterTemplates(self.app, None)

    def test_ct_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Plugin name', 'Plugin version']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('template', '0647061f-ab98-4c89-84e0-30738ea55750',
                          'fake', '0.1')]
        self.assertEqual(expected_data, list(data))

    def test_ct_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Plugin name', 'Plugin version',
                            'Node groups', 'Description']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('template', '0647061f-ab98-4c89-84e0-30738ea55750',
                          'fake', '0.1', 'fakeng:2',
                          'Cluster template for tests')]
        self.assertEqual(expected_data, list(data))

    def test_ct_list_extra_search_opts(self):
        arglist = ['--plugin', 'fake', '--plugin-version', '0.1', '--name',
                   'templ']
        verifylist = [('plugin', 'fake'), ('plugin_version', '0.1'),
                      ('name', 'templ')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Plugin name', 'Plugin version']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('template', '0647061f-ab98-4c89-84e0-30738ea55750',
                          'fake', '0.1')]
        self.assertEqual(expected_data, list(data))


class TestShowClusterTemplate(TestClusterTemplates):
    def setUp(self):
        super(TestShowClusterTemplate, self).setUp()
        self.ct_mock.find_unique.return_value = api_ct.ClusterTemplate(
            None, CT_INFO)

        # Command to test
        self.cmd = osc_ct.ShowClusterTemplate(self.app, None)

    def test_ct_show(self):
        arglist = ['template']
        verifylist = [('cluster_template', 'template')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ct_mock.find_unique.assert_called_once_with(name='template')

        # Check that columns are correct
        expected_columns = ('Anti affinity', 'Description',
                            'Domain name', 'Id', 'Is default',
                            'Is protected', 'Is public', 'Name', 'Node groups',
                            'Plugin name', 'Plugin version', 'Use autoconfig')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = (
            '', 'Cluster template for tests', 'domain.org.',
            '0647061f-ab98-4c89-84e0-30738ea55750', False, False, False,
            'template', 'fakeng:2', 'fake', '0.1', True)
        self.assertEqual(expected_data, data)


class TestDeleteClusterTemplate(TestClusterTemplates):
    def setUp(self):
        super(TestDeleteClusterTemplate, self).setUp()
        self.ct_mock.find_unique.return_value = api_ct.ClusterTemplate(
            None, CT_INFO)

        # Command to test
        self.cmd = osc_ct.DeleteClusterTemplate(self.app, None)

    def test_ct_delete(self):
        arglist = ['template']
        verifylist = [('cluster_template', ['template'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ct_mock.delete.assert_called_once_with(
            '0647061f-ab98-4c89-84e0-30738ea55750')


class TestUpdateClusterTemplate(TestClusterTemplates):
    # TODO(apavlov): check for update with --json
    def setUp(self):
        super(TestUpdateClusterTemplate, self).setUp()
        self.ct_mock.update.return_value = api_ct.ClusterTemplate(
            None, CT_INFO)
        self.ct_mock.find_unique.return_value = api_ct.ClusterTemplate(
            None, CT_INFO)
        self.ngt_mock.find_unique.return_value = api_ngt.NodeGroupTemplate(
            None, CT_INFO['node_groups'][0])

        # Command to test
        self.cmd = osc_ct.UpdateClusterTemplate(self.app, None)

    def test_ct_update_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_ct_update_nothing_updated(self):
        arglist = ['template']
        verifylist = [('cluster_template', 'template')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.ct_mock.update.assert_called_once_with(
            '0647061f-ab98-4c89-84e0-30738ea55750')

    def test_ct_update_all_options(self):
        arglist = ['template', '--name', 'template', '--node-groups',
                   'fakeng:2', '--anti-affinity', 'datanode',
                   '--description', 'descr', '--autoconfig-enable',
                   '--public', '--protected', '--domain-name', 'domain.org.']

        verifylist = [('cluster_template', 'template'), ('name', 'template'),
                      ('node_groups', ['fakeng:2']),
                      ('description', 'descr'), ('use_autoconfig', True),
                      ('is_public', True), ('is_protected', True),
                      ('domain_name', 'domain.org.')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ct_mock.update.assert_called_once_with(
            '0647061f-ab98-4c89-84e0-30738ea55750', description='descr',
            plugin_version='0.1', is_protected=True, is_public=True,
            name='template',
            node_groups=[
                {'count': 2, 'name': 'fakeng',
                 'node_group_template_id':
                     'd29631fc-0fad-434b-80aa-7a3e9526f57c'}],
            plugin_name='fake', use_autoconfig=True, domain_name='domain.org.')

        # Check that columns are correct
        expected_columns = ('Anti affinity', 'Description',
                            'Domain name', 'Id', 'Is default',
                            'Is protected', 'Is public', 'Name', 'Node groups',
                            'Plugin name', 'Plugin version', 'Use autoconfig')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('', 'Cluster template for tests', 'domain.org.',
                         '0647061f-ab98-4c89-84e0-30738ea55750', False, False,
                         False, 'template', 'fakeng:2', 'fake', '0.1', True)
        self.assertEqual(expected_data, data)

    def test_ct_update_private_unprotected(self):
        arglist = ['template', '--private', '--unprotected']
        verifylist = [('cluster_template', 'template'),
                      ('is_protected', False), ('is_public', False)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.ct_mock.update.assert_called_once_with(
            '0647061f-ab98-4c89-84e0-30738ea55750', is_protected=False,
            is_public=False)
