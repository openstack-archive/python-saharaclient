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

from saharaclient.api import node_group_templates as api_ngt
from saharaclient.osc.v2 import node_group_templates as osc_ngt
from saharaclient.tests.unit.osc.v1 import fakes


NGT_INFO = {
    "node_processes": [
        "namenode",
        "tasktracker"
    ],
    "name": "template",
    "tenant_id": "tenant_id",
    "availability_zone": 'av_zone',
    "use_autoconfig": True,
    "plugin_version": "0.1",
    "shares": None,
    "is_default": False,
    "description": 'description',
    "node_configs": {},
    "is_proxy_gateway": False,
    "auto_security_group": True,
    "volume_type": None,
    "volumes_size": 2,
    "volume_mount_prefix": "/volumes/disk",
    "plugin_name": "fake",
    "is_protected": False,
    "security_groups": None,
    "floating_ip_pool": "floating_pool",
    "is_public": True,
    "id": "ng_id",
    "flavor_id": "flavor_id",
    "volumes_availability_zone": None,
    "volumes_per_node": 2,
    "volume_local_to_instance": False,
    "boot_from_volume": False,
    "boot_volume_type": None,
    "boot_volume_availability_zone": None,
    "boot_volume_local_to_instance": False
}


class TestNodeGroupTemplates(fakes.TestDataProcessing):
    def setUp(self):
        super(TestNodeGroupTemplates, self).setUp()
        self.app.api_version['data_processing'] = '2'
        self.ngt_mock = (
            self.app.client_manager.data_processing.node_group_templates)
        self.ngt_mock.reset_mock()


class TestCreateNodeGroupTemplate(TestNodeGroupTemplates):
    # TODO(apavlov): check for creation with --json
    def setUp(self):
        super(TestCreateNodeGroupTemplate, self).setUp()
        self.ngt_mock.create.return_value = api_ngt.NodeGroupTemplate(
            None, NGT_INFO)

        self.fl_mock = self.app.client_manager.compute.flavors
        self.fl_mock.get.return_value = mock.Mock(id='flavor_id')
        self.fl_mock.reset_mock()

        # Command to test
        self.cmd = osc_ngt.CreateNodeGroupTemplate(self.app, None)

    def test_ngt_create_minimum_options(self):
        arglist = ['--name', 'template', '--plugin', 'fake',
                   '--plugin-version', '0.1', '--processes', 'namenode',
                   'tasktracker', '--flavor', 'flavor_id']
        verifylist = [('name', 'template'), ('plugin', 'fake'),
                      ('plugin_version', '0.1'), ('flavor', 'flavor_id'),
                      ('processes', ['namenode', 'tasktracker'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ngt_mock.create.assert_called_once_with(
            auto_security_group=False, availability_zone=None,
            description=None, flavor_id='flavor_id', floating_ip_pool=None,
            plugin_version='0.1', is_protected=False, is_proxy_gateway=False,
            is_public=False, name='template',
            node_processes=['namenode', 'tasktracker'], plugin_name='fake',
            security_groups=None, use_autoconfig=False,
            volume_local_to_instance=False,
            volume_type=None, volumes_availability_zone=None,
            volumes_per_node=None, volumes_size=None, shares=None,
            node_configs=None, volume_mount_prefix=None,
            boot_from_volume=False,
            boot_volume_type=None,
            boot_volume_availability_zone=None,
            boot_volume_local_to_instance=False)

    def test_ngt_create_all_options(self):
        arglist = ['--name', 'template', '--plugin', 'fake',
                   '--plugin-version', '0.1', '--processes', 'namenode',
                   'tasktracker', '--security-groups', 'secgr',
                   '--auto-security-group', '--availability-zone', 'av_zone',
                   '--flavor', 'flavor_id', '--floating-ip-pool',
                   'floating_pool', '--volumes-per-node',
                   '2', '--volumes-size', '2', '--volumes-type', 'type',
                   '--volumes-availability-zone', 'vavzone',
                   '--volumes-mount-prefix', '/volume/asd',
                   '--volumes-locality', '--description', 'descr',
                   '--autoconfig', '--proxy-gateway', '--public',
                   '--protected', '--boot-from-volume',
                   '--boot-volume-type', 'volume2',
                   '--boot-volume-availability-zone', 'ceph',
                   '--boot-volume-local-to-instance']

        verifylist = [('name', 'template'), ('plugin', 'fake'),
                      ('plugin_version', '0.1'),
                      ('processes', ['namenode', 'tasktracker']),
                      ('security_groups', ['secgr']),
                      ('auto_security_group', True),
                      ('availability_zone', 'av_zone'),
                      ('flavor', 'flavor_id'),
                      ('floating_ip_pool', 'floating_pool'),
                      ('volumes_per_node', 2), ('volumes_size', 2),
                      ('volumes_type', 'type'),
                      ('volumes_availability_zone', 'vavzone'),
                      ('volumes_mount_prefix', '/volume/asd'),
                      ('volumes_locality', True), ('description', 'descr'),
                      ('autoconfig', True), ('proxy_gateway', True),
                      ('public', True), ('protected', True),
                      ('boot_from_volume', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ngt_mock.create.assert_called_once_with(
            auto_security_group=True, availability_zone='av_zone',
            description='descr', flavor_id='flavor_id',
            floating_ip_pool='floating_pool', plugin_version='0.1',
            is_protected=True, is_proxy_gateway=True, is_public=True,
            name='template', node_processes=['namenode', 'tasktracker'],
            plugin_name='fake', security_groups=['secgr'], use_autoconfig=True,
            volume_local_to_instance=True, volume_type='type',
            volumes_availability_zone='vavzone', volumes_per_node=2,
            volumes_size=2, shares=None, node_configs=None,
            volume_mount_prefix='/volume/asd', boot_from_volume=True,
            boot_volume_type='volume2',
            boot_volume_availability_zone='ceph',
            boot_volume_local_to_instance=True)

        # Check that columns are correct
        expected_columns = (
            'Auto security group', 'Availability zone', 'Boot from volume',
            'Description', 'Flavor id', 'Floating ip pool', 'Id',
            'Is default', 'Is protected', 'Is proxy gateway', 'Is public',
            'Name', 'Node processes', 'Plugin name', 'Plugin version',
            'Security groups', 'Use autoconfig', 'Volume local to instance',
            'Volume mount prefix', 'Volume type', 'Volumes availability zone',
            'Volumes per node', 'Volumes size')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = (
            True, 'av_zone', False, 'description', 'flavor_id',
            'floating_pool', 'ng_id', False, False, False, True,
            'template', 'namenode, tasktracker', 'fake', '0.1', None, True,
            False, '/volumes/disk', None, None, 2, 2)
        self.assertEqual(expected_data, data)


class TestListNodeGroupTemplates(TestNodeGroupTemplates):
    def setUp(self):
        super(TestListNodeGroupTemplates, self).setUp()
        self.ngt_mock.list.return_value = [api_ngt.NodeGroupTemplate(
            None, NGT_INFO)]

        # Command to test
        self.cmd = osc_ngt.ListNodeGroupTemplates(self.app, None)

    def test_ngt_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Plugin name', 'Plugin version']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('template', 'ng_id', 'fake', '0.1')]
        self.assertEqual(expected_data, list(data))

    def test_ngt_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Plugin name', 'Plugin version',
                            'Node processes', 'Description']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('template', 'ng_id', 'fake', '0.1',
                          'namenode, tasktracker', 'description')]
        self.assertEqual(expected_data, list(data))

    def test_ngt_list_extra_search_opts(self):
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
        expected_data = [('template', 'ng_id', 'fake', '0.1')]
        self.assertEqual(expected_data, list(data))


class TestShowNodeGroupTemplate(TestNodeGroupTemplates):
    def setUp(self):
        super(TestShowNodeGroupTemplate, self).setUp()
        self.ngt_mock.find_unique.return_value = api_ngt.NodeGroupTemplate(
            None, NGT_INFO)

        # Command to test
        self.cmd = osc_ngt.ShowNodeGroupTemplate(self.app, None)

    def test_ngt_show(self):
        arglist = ['template']
        verifylist = [('node_group_template', 'template')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ngt_mock.find_unique.assert_called_once_with(name='template')

        # Check that columns are correct
        expected_columns = (
            'Auto security group', 'Availability zone', 'Boot from volume',
            'Description', 'Flavor id', 'Floating ip pool', 'Id',
            'Is default', 'Is protected', 'Is proxy gateway', 'Is public',
            'Name', 'Node processes', 'Plugin name', 'Plugin version',
            'Security groups', 'Use autoconfig', 'Volume local to instance',
            'Volume mount prefix', 'Volume type', 'Volumes availability zone',
            'Volumes per node', 'Volumes size')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = (
            True, 'av_zone', False, 'description', 'flavor_id',
            'floating_pool', 'ng_id', False, False, False, True,
            'template', 'namenode, tasktracker', 'fake', '0.1', None, True,
            False, '/volumes/disk', None, None, 2, 2)
        self.assertEqual(expected_data, data)


class TestDeleteNodeGroupTemplate(TestNodeGroupTemplates):
    def setUp(self):
        super(TestDeleteNodeGroupTemplate, self).setUp()
        self.ngt_mock.find_unique.return_value = api_ngt.NodeGroupTemplate(
            None, NGT_INFO)

        # Command to test
        self.cmd = osc_ngt.DeleteNodeGroupTemplate(self.app, None)

    def test_ngt_delete(self):
        arglist = ['template']
        verifylist = [('node_group_template', ['template'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ngt_mock.delete.assert_called_once_with('ng_id')


class TestUpdateNodeGroupTemplate(TestNodeGroupTemplates):
    # TODO(apavlov): check for update with --json
    def setUp(self):
        super(TestUpdateNodeGroupTemplate, self).setUp()
        self.ngt_mock.find_unique.return_value = api_ngt.NodeGroupTemplate(
            None, NGT_INFO)
        self.ngt_mock.update.return_value = api_ngt.NodeGroupTemplate(
            None, NGT_INFO)

        self.fl_mock = self.app.client_manager.compute.flavors
        self.fl_mock.get.return_value = mock.Mock(id='flavor_id')
        self.fl_mock.reset_mock()

        # Command to test
        self.cmd = osc_ngt.UpdateNodeGroupTemplate(self.app, None)

    def test_ngt_update_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_ngt_update_nothing_updated(self):
        arglist = ['template']
        verifylist = [('node_group_template', 'template')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ngt_mock.update.assert_called_once_with('ng_id')

    def test_ngt_update_all_options(self):
        arglist = ['template', '--name', 'template', '--plugin', 'fake',
                   '--plugin-version', '0.1', '--processes', 'namenode',
                   'tasktracker', '--security-groups', 'secgr',
                   '--auto-security-group-enable',
                   '--availability-zone', 'av_zone', '--flavor', 'flavor_id',
                   '--floating-ip-pool', 'floating_pool', '--volumes-per-node',
                   '2', '--volumes-size', '2', '--volumes-type', 'type',
                   '--volumes-availability-zone', 'vavzone',
                   '--volumes-mount-prefix', '/volume/asd',
                   '--volumes-locality-enable', '--description', 'descr',
                   '--autoconfig-enable', '--proxy-gateway-enable', '--public',
                   '--protected', '--boot-from-volume-enable',
                   '--boot-volume-type', 'volume2',
                   '--boot-volume-availability-zone', 'ceph',
                   '--boot-volume-local-to-instance-enable']

        verifylist = [('node_group_template', 'template'),
                      ('name', 'template'), ('plugin', 'fake'),
                      ('plugin_version', '0.1'),
                      ('processes', ['namenode', 'tasktracker']),
                      ('security_groups', ['secgr']),
                      ('use_auto_security_group', True),
                      ('availability_zone', 'av_zone'),
                      ('flavor', 'flavor_id'),
                      ('floating_ip_pool', 'floating_pool'),
                      ('volumes_per_node', 2), ('volumes_size', 2),
                      ('volumes_type', 'type'),
                      ('volumes_availability_zone', 'vavzone'),
                      ('volumes_mount_prefix', '/volume/asd'),
                      ('volume_locality', True),
                      ('description', 'descr'), ('use_autoconfig', True),
                      ('is_proxy_gateway', True),
                      ('is_public', True), ('is_protected', True),
                      ('boot_from_volume', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ngt_mock.update.assert_called_once_with(
            'ng_id',
            auto_security_group=True, availability_zone='av_zone',
            description='descr', flavor_id='flavor_id',
            floating_ip_pool='floating_pool', plugin_version='0.1',
            is_protected=True, is_proxy_gateway=True, is_public=True,
            name='template', node_processes=['namenode', 'tasktracker'],
            plugin_name='fake', security_groups=['secgr'], use_autoconfig=True,
            volume_local_to_instance=True, volume_type='type',
            volumes_availability_zone='vavzone', volumes_per_node=2,
            volumes_size=2, volume_mount_prefix='/volume/asd',
            boot_from_volume=True,
            boot_volume_type='volume2',
            boot_volume_availability_zone='ceph',
            boot_volume_local_to_instance=True)

        # Check that columns are correct
        expected_columns = (
            'Auto security group', 'Availability zone', 'Boot from volume',
            'Description', 'Flavor id', 'Floating ip pool', 'Id',
            'Is default', 'Is protected', 'Is proxy gateway', 'Is public',
            'Name', 'Node processes', 'Plugin name', 'Plugin version',
            'Security groups', 'Use autoconfig', 'Volume local to instance',
            'Volume mount prefix', 'Volume type', 'Volumes availability zone',
            'Volumes per node', 'Volumes size')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = (
            True, 'av_zone', False, 'description', 'flavor_id',
            'floating_pool', 'ng_id', False, False, False, True,
            'template', 'namenode, tasktracker', 'fake', '0.1', None, True,
            False, '/volumes/disk', None, None, 2, 2)
        self.assertEqual(expected_data, data)

    def test_ngt_update_private_unprotected(self):
        arglist = ['template', '--private', '--unprotected']
        verifylist = [('node_group_template', 'template'),
                      ('is_public', False), ('is_protected', False)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.ngt_mock.update.assert_called_once_with(
            'ng_id', is_protected=False, is_public=False)
