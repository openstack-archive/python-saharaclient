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

from saharaclient.api.v2 import job_templates as api_j
from saharaclient.osc.v2 import job_templates as osc_j
from saharaclient.tests.unit.osc.v1 import test_job_templates as tjt_v1

JOB_TEMPLATE_INFO = {
    "is_public": False,
    "id": "job_id",
    "name": "pig-job",
    "description": "Job for test",
    "interface": [],
    "libs": [
        {
            "id": "lib_id",
            "name": "lib"
        }
    ],
    "type": "Pig",
    "is_protected": False,
    "mains": [
        {
            "id": "main_id",
            "name": "main"
        }
    ]
}


class TestJobTemplates(tjt_v1.TestJobTemplates):
    def setUp(self):
        super(TestJobTemplates, self).setUp()
        self.app.api_version['data_processing'] = '2'
        self.job_mock = self.app.client_manager.data_processing.job_templates
        self.job_mock.reset_mock()


class TestCreateJobTemplate(TestJobTemplates):
    # TODO(apavlov): check for creation with --interface
    def setUp(self):
        super(TestCreateJobTemplate, self).setUp()
        self.job_mock.create.return_value = api_j.JobTemplate(
            None, JOB_TEMPLATE_INFO)
        self.jb_mock = self.app.client_manager.data_processing.job_binaries
        self.jb_mock.find_unique.return_value = mock.Mock(id='jb_id')
        self.jb_mock.reset_mock()

        # Command to test
        self.cmd = osc_j.CreateJobTemplate(self.app, None)

    def test_job_template_create_minimum_options(self):
        arglist = ['--name', 'pig-job', '--type', 'Pig']
        verifylist = [('name', 'pig-job'), ('type', 'Pig')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.job_mock.create.assert_called_once_with(
            description=None, interface=None, is_protected=False,
            is_public=False, libs=None, mains=None, name='pig-job', type='Pig')

    def test_job_template_create_all_options(self):
        arglist = ['--name', 'pig-job', '--type', 'Pig', '--mains', 'main',
                   '--libs', 'lib', '--description', 'descr', '--public',
                   '--protected']

        verifylist = [('name', 'pig-job'), ('type', 'Pig'),
                      ('mains', ['main']), ('libs', ['lib']),
                      ('description', 'descr'), ('public', True),
                      ('protected', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.job_mock.create.assert_called_once_with(
            description='descr', interface=None, is_protected=True,
            is_public=True, libs=['jb_id'], mains=['jb_id'], name='pig-job',
            type='Pig')

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Is protected', 'Is public',
                            'Libs', 'Mains', 'Name', 'Type')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('Job for test', 'job_id', False, False, 'lib:lib_id',
                         'main:main_id', 'pig-job', 'Pig')
        self.assertEqual(expected_data, data)


class TestListJobTemplates(TestJobTemplates):
    def setUp(self):
        super(TestListJobTemplates, self).setUp()
        self.job_mock.list.return_value = [api_j.JobTemplate(
            None, JOB_TEMPLATE_INFO)]

        # Command to test
        self.cmd = osc_j.ListJobTemplates(self.app, None)

    def test_job_templates_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Type']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('pig-job', 'job_id', 'Pig')]
        self.assertEqual(expected_data, list(data))

    def test_job_template_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Type', 'Description', 'Is public',
                            'Is protected']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('pig-job', 'job_id', 'Pig', 'Job for test',
                          False, False)]
        self.assertEqual(expected_data, list(data))

    def test_job_template_list_extra_search_opts(self):
        arglist = ['--type', 'Pig', '--name', 'pig']
        verifylist = [('type', 'Pig'), ('name', 'pig')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Type']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('pig-job', 'job_id', 'Pig')]
        self.assertEqual(expected_data, list(data))


class TestShowJobTemplate(TestJobTemplates):
    def setUp(self):
        super(TestShowJobTemplate, self).setUp()
        self.job_mock.find_unique.return_value = api_j.JobTemplate(
            None, JOB_TEMPLATE_INFO)

        # Command to test
        self.cmd = osc_j.ShowJobTemplate(self.app, None)

    def test_job_template_show(self):
        arglist = ['pig-job']
        verifylist = [('job_template', 'pig-job')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.job_mock.find_unique.assert_called_once_with(name='pig-job')

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Is protected', 'Is public',
                            'Libs', 'Mains', 'Name', 'Type')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('Job for test', 'job_id', False, False, 'lib:lib_id',
                         'main:main_id', 'pig-job', 'Pig')
        self.assertEqual(expected_data, data)


class TestDeleteJobTemplate(TestJobTemplates):
    def setUp(self):
        super(TestDeleteJobTemplate, self).setUp()
        self.job_mock.find_unique.return_value = api_j.JobTemplate(
            None, JOB_TEMPLATE_INFO)

        # Command to test
        self.cmd = osc_j.DeleteJobTemplate(self.app, None)

    def test_job_template_delete(self):
        arglist = ['pig-job']
        verifylist = [('job_template', ['pig-job'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.job_mock.delete.assert_called_once_with('job_id')


class TestUpdateJobTemplate(TestJobTemplates):
    def setUp(self):
        super(TestUpdateJobTemplate, self).setUp()
        self.job_mock.find_unique.return_value = api_j.JobTemplate(
            None, JOB_TEMPLATE_INFO)
        self.job_mock.update.return_value = mock.Mock(
            job_template=JOB_TEMPLATE_INFO.copy())

        # Command to test
        self.cmd = osc_j.UpdateJobTemplate(self.app, None)

    def test_job_template_update_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_job_template_update_nothing_updated(self):
        arglist = ['pig-job']

        verifylist = [('job_template', 'pig-job')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.job_mock.update.assert_called_once_with('job_id')

    def test_job_template_update_all_options(self):
        arglist = ['pig-job', '--name', 'pig-job', '--description', 'descr',
                   '--public', '--protected']

        verifylist = [('job_template', 'pig-job'), ('name', 'pig-job'),
                      ('description', 'descr'), ('is_public', True),
                      ('is_protected', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.job_mock.update.assert_called_once_with(
            'job_id', description='descr', is_protected=True, is_public=True,
            name='pig-job')

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Is protected', 'Is public',
                            'Libs', 'Mains', 'Name', 'Type')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('Job for test', 'job_id', False, False, 'lib:lib_id',
                         'main:main_id', 'pig-job', 'Pig')
        self.assertEqual(expected_data, data)

    def test_job_template_update_private_unprotected(self):
        arglist = ['pig-job', '--private', '--unprotected']

        verifylist = [('job_template', 'pig-job'), ('is_public', False),
                      ('is_protected', False)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.job_mock.update.assert_called_once_with(
            'job_id', is_protected=False, is_public=False)
