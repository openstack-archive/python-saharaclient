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

from openstackclient.tests import utils as osc_utils

from saharaclient.api import data_sources as api_ds
from saharaclient.osc.v1 import data_sources as osc_ds
from saharaclient.tests.unit.osc.v1 import fakes


DS_INFO = {'id': 'id', 'name': 'source', 'type': 'swift',
           'url': 'swift://container.sahara/object',
           'description': 'Data Source for tests'}


class TestDataSources(fakes.TestDataProcessing):
    def setUp(self):
        super(TestDataSources, self).setUp()
        self.ds_mock = (
            self.app.client_manager.data_processing.data_sources)
        self.ds_mock.reset_mock()


class TestCreateDataSource(TestDataSources):
    def setUp(self):
        super(TestCreateDataSource, self).setUp()
        self.ds_mock.create.return_value = api_ds.DataSources(
            None, DS_INFO)

        # Command to test
        self.cmd = osc_ds.CreateDataSource(self.app, None)

    def test_data_sources_create_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_data_sources_create_required_options(self):
        arglist = ['source', '--type', 'swift', '--url',
                   'swift://container.sahara/object']
        verifylist = [('name', 'source'), ('type', 'swift'),
                      ('url', 'swift://container.sahara/object')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that data source was created with correct arguments
        called_args = {'credential_pass': None, 'credential_user': None,
                       'data_source_type': 'swift', 'name': 'source',
                       'description': '',
                       'url': 'swift://container.sahara/object'}
        self.ds_mock.create.assert_called_once_with(**called_args)

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Name', 'Type', 'Url')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('Data Source for tests', 'id', 'source', 'swift',
                         'swift://container.sahara/object')
        self.assertEqual(expected_data, data)

    def test_data_sources_create_all_options(self):
        arglist = ['source', '--type', 'swift', '--url',
                   'swift://container.sahara/object', '--username', 'user',
                   '--password', 'pass', '--description',
                   'Data Source for tests']
        verifylist = [('name', 'source'), ('type', 'swift'),
                      ('url', 'swift://container.sahara/object'),
                      ('username', 'user'), ('password', 'pass'),
                      ('description', 'Data Source for tests')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that data source was created with correct arguments
        called_args = {'credential_pass': 'pass', 'credential_user': 'user',
                       'data_source_type': 'swift', 'name': 'source',
                       'description': 'Data Source for tests',
                       'url': 'swift://container.sahara/object'}
        self.ds_mock.create.assert_called_once_with(**called_args)

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Name', 'Type', 'Url')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('Data Source for tests', 'id', 'source', 'swift',
                         'swift://container.sahara/object')
        self.assertEqual(expected_data, data)


class TestListDataSources(TestDataSources):
    def setUp(self):
        super(TestListDataSources, self).setUp()
        self.ds_mock.list.return_value = [api_ds.DataSources(
            None, DS_INFO)]

        # Command to test
        self.cmd = osc_ds.ListDataSources(self.app, None)

    def test_data_sources_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Type']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('source', 'id', 'swift')]
        self.assertEqual(expected_data, list(data))

    def test_data_sources_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Type', 'Url', 'Description']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('source', 'id', 'swift',
                          'swift://container.sahara/object',
                          'Data Source for tests')]
        self.assertEqual(expected_data, list(data))


class TestShowDataSource(TestDataSources):
    def setUp(self):
        super(TestShowDataSource, self).setUp()
        self.ds_mock.get.return_value = api_ds.DataSources(
            None, DS_INFO)

        # Command to test
        self.cmd = osc_ds.ShowDataSource(self.app, None)

    def test_data_sources_show(self):
        arglist = ['source']
        verifylist = [('data_source', 'source')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments was passed
        self.ds_mock.get.assert_called_once_with('source')

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Name', 'Type', 'Url')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ['Data Source for tests', 'id', 'source', 'swift',
                         'swift://container.sahara/object']
        self.assertEqual(expected_data, list(data))


class TestDeleteDataSource(TestDataSources):
    def setUp(self):
        super(TestDeleteDataSource, self).setUp()
        self.ds_mock.get.return_value = api_ds.DataSources(
            None, DS_INFO)

        # Command to test
        self.cmd = osc_ds.DeleteDataSource(self.app, None)

    def test_data_sources_delete(self):
        arglist = ['source']
        verifylist = [('data_source', 'source')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments was passed
        self.ds_mock.delete.assert_called_once_with('id')
