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

from saharaclient.api import plugins as api_plugins
from saharaclient.osc.v1 import plugins as osc_plugins
from saharaclient.tests.unit.osc.v1 import fakes


PLUGIN_INFO = {'name': 'fake',
               'title': 'Fake Plugin',
               'versions': ['0.1', '0.2'],
               'description': 'Plugin for tests'}


class TestPlugins(fakes.TestDataProcessing):
    def setUp(self):
        super(TestPlugins, self).setUp()
        self.plugins_mock = self.app.client_manager.data_processing.plugins
        self.plugins_mock.reset_mock()


class TestListPlugins(TestPlugins):
    def setUp(self):
        super(TestListPlugins, self).setUp()
        self.plugins_mock.list.return_value = [api_plugins.Plugin(
            None, PLUGIN_INFO)]

        # Command to test
        self.cmd = osc_plugins.ListPlugins(self.app, None)

    def test_plugins_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Versions']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('fake', '0.1, 0.2')]
        self.assertEqual(expected_data, list(data))

    def test_plugins_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Title', 'Versions', 'Description']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('fake', 'Fake Plugin', '0.1, 0.2',
                          'Plugin for tests')]
        self.assertEqual(expected_data, list(data))


class TestShowPlugin(TestPlugins):
    def setUp(self):
        super(TestShowPlugin, self).setUp()
        self.plugins_mock.get.return_value = api_plugins.Plugin(
            None, PLUGIN_INFO)

        # Command to test
        self.cmd = osc_plugins.ShowPlugin(self.app, None)

    def test_plugin_show(self):
        arglist = ['fake']
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments was passed
        self.plugins_mock.get.assert_called_once_with('fake')

        # Check that columns are correct
        expected_columns = ('description', 'name', 'title', 'versions')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('Plugin for tests', 'fake', 'Fake Plugin', '0.1, 0.2')
        self.assertEqual(expected_data, data)


class TestGetPluginConfigs(TestPlugins):
    def setUp(self):
        super(TestGetPluginConfigs, self).setUp()
        self.plugins_mock.get_version_details.return_value = (
            api_plugins.Plugin(None, PLUGIN_INFO))

        # Command to test
        self.cmd = osc_plugins.GetPluginConfigs(self.app, None)

    @mock.patch('oslo_serialization.jsonutils.dump')
    def test_get_plugin_configs_default_file(self, p_dump):
        m_open = mock.mock_open()
        with mock.patch('six.moves.builtins.open', m_open, create=True):
            arglist = ['fake', '0.1']
            verifylist = [('plugin', 'fake'), ('version', '0.1')]

            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            self.cmd.take_action(parsed_args)

            # Check that correct arguments was passed
            self.plugins_mock.get_version_details.assert_called_once_with(
                'fake', '0.1')

            args_to_dump = p_dump.call_args[0]
            # Check that the right data will be saved

            self.assertEqual(PLUGIN_INFO, args_to_dump[0])
            # Check that data will be saved to the right file
            self.assertEqual('fake', m_open.call_args[0][0])

    @mock.patch('oslo_serialization.jsonutils.dump')
    def test_get_plugin_configs_specified_file(self, p_dump):
        m_open = mock.mock_open()
        with mock.patch('six.moves.builtins.open', m_open):
            arglist = ['fake', '0.1', '--file', 'testfile']
            verifylist = [('plugin', 'fake'), ('version', '0.1'),
                          ('file', 'testfile')]

            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            self.cmd.take_action(parsed_args)

            # Check that correct arguments was passed
            self.plugins_mock.get_version_details.assert_called_once_with(
                'fake', '0.1')

            args_to_dump = p_dump.call_args[0]
            # Check that the right data will be saved

            self.assertEqual(PLUGIN_INFO, args_to_dump[0])
            # Check that data will be saved to the right file
            self.assertEqual('testfile', m_open.call_args[0][0])
