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
from osc_lib.tests import utils as osc_u
import testtools

from saharaclient.api import job_binaries as api_jb
from saharaclient.osc.v1 import job_binaries as osc_jb
from saharaclient.tests.unit.osc.v1 import test_job_binaries as tjb_v1


JOB_BINARY_INFO = {
    "name": 'job-binary',
    "description": 'descr',
    "id": 'jb_id',
    "is_protected": False,
    "is_public": False,
    "url": 'swift://cont/test'
}


class TestJobBinaries(tjb_v1.TestJobBinaries):
    def setUp(self):
        super(TestJobBinaries, self).setUp()
        self.app.api_version['data_processing'] = '2'
        self.jb_mock = self.app.client_manager.data_processing.job_binaries
        self.jb_mock.reset_mock()


class TestCreateJobBinary(TestJobBinaries):
    # TODO(apavlov): check for creation with --json
    def setUp(self):
        super(TestCreateJobBinary, self).setUp()
        self.jb_mock.create.return_value = api_jb.JobBinaries(
            None, JOB_BINARY_INFO)
        self.jbi_mock = (self.app.client_manager.
                         data_processing.job_binary_internals)
        self.jbi_mock.create.return_value = mock.Mock(id='jbi_id')
        self.jbi_mock.reset_mock()

        # Command to test
        self.cmd = osc_jb.CreateJobBinary(self.app, None)

    def test_job_binary_create_swift_public_protected(self):
        arglist = ['--name', 'job-binary', '--url', 'swift://cont/test',
                   '--username', 'user', '--password', 'pass', '--public',
                   '--protected']
        verifylist = [('name', 'job-binary'), ('url', 'swift://cont/test'),
                      ('username', 'user'), ('password', 'pass'),
                      ('public', True), ('protected', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.jb_mock.create.assert_called_once_with(
            description=None, extra={'password': 'pass', 'user': 'user'},
            is_protected=True, is_public=True, name='job-binary',
            url='swift://cont/test')

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Is protected', 'Is public',
                            'Name', 'Url')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('descr', 'jb_id', False, False, 'job-binary',
                         'swift://cont/test')
        self.assertEqual(expected_data, data)

    def test_job_binary_create_mutual_exclusion(self):
        arglist = ['job-binary', '--name', 'job-binary', '--access-key', 'ak',
                   '--secret-key', 'sk', '--url', 's3://abc/def',
                   '--password', 'pw']

        with testtools.ExpectedException(osc_u.ParserException):
            self.check_parser(self.cmd, arglist, mock.Mock())


class TestListJobBinaries(TestJobBinaries):
    def setUp(self):
        super(TestListJobBinaries, self).setUp()
        self.jb_mock.list.return_value = [api_jb.JobBinaries(
            None, JOB_BINARY_INFO)]

        # Command to test
        self.cmd = osc_jb.ListJobBinaries(self.app, None)

    def test_job_binary_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Url']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('job-binary', 'jb_id', 'swift://cont/test')]
        self.assertEqual(expected_data, list(data))

    def test_job_binary_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Url', 'Description', 'Is public',
                            'Is protected']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('job-binary', 'jb_id', 'swift://cont/test', 'descr',
                          False, False)]
        self.assertEqual(expected_data, list(data))

    def test_job_binary_list_extra_search_opts(self):
        arglist = ['--name', 'bin']
        verifylist = [('name', 'bin')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Url']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('job-binary', 'jb_id', 'swift://cont/test')]
        self.assertEqual(expected_data, list(data))


class TestShowJobBinary(TestJobBinaries):
    def setUp(self):
        super(TestShowJobBinary, self).setUp()
        self.jb_mock.find_unique.return_value = api_jb.JobBinaries(
            None, JOB_BINARY_INFO)

        # Command to test
        self.cmd = osc_jb.ShowJobBinary(self.app, None)

    def test_job_binary_show(self):
        arglist = ['job-binary']
        verifylist = [('job_binary', 'job-binary')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.jb_mock.find_unique.assert_called_once_with(name='job-binary')

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Is protected', 'Is public',
                            'Name', 'Url')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('descr', 'jb_id', False, False, 'job-binary',
                         'swift://cont/test')
        self.assertEqual(expected_data, data)


class TestDeleteJobBinary(TestJobBinaries):
    def setUp(self):
        super(TestDeleteJobBinary, self).setUp()
        self.jb_mock.find_unique.return_value = api_jb.JobBinaries(
            None, JOB_BINARY_INFO)

        # Command to test
        self.cmd = osc_jb.DeleteJobBinary(self.app, None)

    def test_job_binary_delete(self):
        arglist = ['job-binary']
        verifylist = [('job_binary', ['job-binary'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.jb_mock.delete.assert_called_once_with('jb_id')


class TestUpdateJobBinary(TestJobBinaries):
    def setUp(self):
        super(TestUpdateJobBinary, self).setUp()
        self.jb_mock.find_unique.return_value = api_jb.JobBinaries(
            None, JOB_BINARY_INFO)
        self.jb_mock.update.return_value = api_jb.JobBinaries(
            None, JOB_BINARY_INFO)

        # Command to test
        self.cmd = osc_jb.UpdateJobBinary(self.app, None)

    def test_job_binary_update_all_options(self):
        arglist = ['job-binary', '--name', 'job-binary', '--description',
                   'descr', '--username', 'user', '--password', 'pass',
                   '--public', '--protected']

        verifylist = [('job_binary', 'job-binary'), ('name', 'job-binary'),
                      ('description', 'descr'), ('username', 'user'),
                      ('password', 'pass'), ('is_public', True),
                      ('is_protected', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.jb_mock.update.assert_called_once_with(
            'jb_id',
            {'is_public': True, 'description': 'descr', 'is_protected': True,
             'name': 'job-binary',
             'extra': {'password': 'pass', 'user': 'user'}})

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Is protected', 'Is public',
                            'Name', 'Url')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ('descr', 'jb_id', False, False, 'job-binary',
                         'swift://cont/test')
        self.assertEqual(expected_data, data)

    def test_job_binary_update_private_unprotected(self):
        arglist = ['job-binary', '--private', '--unprotected']

        verifylist = [('job_binary', 'job-binary'), ('is_public', False),
                      ('is_protected', False)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.jb_mock.update.assert_called_once_with(
            'jb_id', {'is_public': False, 'is_protected': False})

    def test_job_binary_update_nothing_updated(self):
        arglist = ['job-binary']

        verifylist = [('job_binary', 'job-binary')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.jb_mock.update.assert_called_once_with(
            'jb_id', {})

    def test_job_binary_update_mutual_exclusion(self):
        arglist = ['job-binary', '--name', 'job-binary', '--access-key', 'ak',
                   '--secret-key', 'sk', '--url', 's3://abc/def',
                   '--password', 'pw']

        with testtools.ExpectedException(osc_u.ParserException):
            self.check_parser(self.cmd, arglist, mock.Mock())


class TestDownloadJobBinary(TestJobBinaries):
    def setUp(self):
        super(TestDownloadJobBinary, self).setUp()
        self.jb_mock.get_file.return_value = 'data'
        self.jb_mock.find_unique.return_value = api_jb.JobBinaries(
            None, JOB_BINARY_INFO)

        # Command to test
        self.cmd = osc_jb.DownloadJobBinary(self.app, None)

    def test_download_job_binary_default_file(self):
        m_open = mock.mock_open()
        with mock.patch('six.moves.builtins.open', m_open, create=True):
            arglist = ['job-binary']
            verifylist = [('job_binary', 'job-binary')]

            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            self.cmd.take_action(parsed_args)

            # Check that correct arguments was passed
            self.jb_mock.get_file.assert_called_once_with(
                'jb_id')

            # Check that data will be saved to the right file
            self.assertEqual('job-binary', m_open.call_args[0][0])

    def test_download_job_binary_specified_file(self):
        m_open = mock.mock_open()
        with mock.patch('six.moves.builtins.open', m_open, create=True):
            arglist = ['job-binary', '--file', 'test']
            verifylist = [('job_binary', 'job-binary'), ('file', 'test')]

            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            self.cmd.take_action(parsed_args)

            # Check that correct arguments was passed
            self.jb_mock.get_file.assert_called_once_with(
                'jb_id')

            # Check that data will be saved to the right file
            self.assertEqual('test', m_open.call_args[0][0])
