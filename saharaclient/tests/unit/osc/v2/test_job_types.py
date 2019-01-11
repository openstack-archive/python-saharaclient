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

from saharaclient.api import job_types as api_jt
from saharaclient.api.v2 import job_templates as api_job_templates
from saharaclient.osc.v2 import job_types as osc_jt
from saharaclient.tests.unit.osc.v1 import test_job_types as tjt_v1

JOB_TYPE_INFO = {
    "name": 'Pig',
    "plugins": [
        {
            'versions': {
                '0.1': {},
                '0.2': {}
            },
            'name': 'fake'
        },
        {
            'versions': {
                '6.2.2': {}
            },
            'name': 'wod'
        }
    ]
}


class TestJobTypes(tjt_v1.TestJobTypes):
    def setUp(self):
        super(TestJobTypes, self).setUp()
        self.app.api_version['data_processing'] = '2'
        self.job_template_mock = (
            self.app.client_manager.data_processing.job_templates)
        self.jt_mock = self.app.client_manager.data_processing.job_types
        self.jt_mock.reset_mock()
        self.job_template_mock.reset_mock()


class TestListJobTemplates(TestJobTypes):
    def setUp(self):
        super(TestListJobTemplates, self).setUp()
        self.jt_mock.list.return_value = [api_jt.JobType(None, JOB_TYPE_INFO)]

        # Command to test
        self.cmd = osc_jt.ListJobTypes(self.app, None)

    def test_job_types_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Plugins']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('Pig', 'fake(0.1, 0.2), wod(6.2.2)')]
        self.assertEqual(expected_data, list(data))

    def test_job_types_list_extra_search_opts(self):
        arglist = ['--type', 'Pig', '--plugin', 'fake', '--plugin-version',
                   '0.1']
        verifylist = [('type', 'Pig'), ('plugin', 'fake'),
                      ('plugin_version', '0.1')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Plugins']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('Pig', 'fake(0.1, 0.2), wod(6.2.2)')]
        self.assertEqual(expected_data, list(data))


class TestGetJobTypeConfigs(TestJobTypes):
    def setUp(self):
        super(TestGetJobTypeConfigs, self).setUp()
        self.job_template_mock.get_configs.return_value = (
            api_job_templates.JobTemplate(None, JOB_TYPE_INFO))

        # Command to test
        self.cmd = osc_jt.GetJobTypeConfigs(self.app, None)

    @mock.patch('oslo_serialization.jsonutils.dump')
    def test_get_job_type_configs_default_file(self, p_dump):
        m_open = mock.mock_open()
        with mock.patch('six.moves.builtins.open', m_open, create=True):
            arglist = ['Pig']
            verifylist = [('job_type', 'Pig')]

            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            self.cmd.take_action(parsed_args)

            # Check that correct arguments was passed
            self.job_template_mock.get_configs.assert_called_once_with(
                'Pig')

            args_to_dump = p_dump.call_args[0]
            # Check that the right data will be saved

            self.assertEqual(JOB_TYPE_INFO, args_to_dump[0])
            # Check that data will be saved to the right file
            self.assertEqual('Pig', m_open.call_args[0][0])

    @mock.patch('oslo_serialization.jsonutils.dump')
    def test_get_job_type_configs_specified_file(self, p_dump):
        m_open = mock.mock_open()
        with mock.patch('six.moves.builtins.open', m_open):
            arglist = ['Pig', '--file', 'testfile']
            verifylist = [('job_type', 'Pig'), ('file', 'testfile')]

            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            self.cmd.take_action(parsed_args)

            # Check that correct arguments was passed
            self.job_template_mock.get_configs.assert_called_once_with(
                'Pig')

            args_to_dump = p_dump.call_args[0]
            # Check that the right data will be saved

            self.assertEqual(JOB_TYPE_INFO, args_to_dump[0])
            # Check that data will be saved to the right file
            self.assertEqual('testfile', m_open.call_args[0][0])
