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

from saharaclient.api import job_binary_internals as jbi
from saharaclient.tests.unit import base


class JobBinaryInternalTest(base.BaseTestCase):
    body = {
        'name': 'name',
        'datasize': '123',
        'id': 'id'
    }

    @mock.patch('requests.put')
    def test_create_job_binary_internal(self, mput):
        mput.return_value = base.FakeResponse(202, self.body,
                                              'job_binary_internal')

        resp = self.client.job_binary_internals.create('name', 'data')

        self.assertEqual('http://localhost:8386/job-binary-internals/name',
                         mput.call_args[0][0])

        self.assertEqual('data', mput.call_args[0][1])
        self.assertIsInstance(resp, jbi.JobBinaryInternal)
        self.assertFields(self.body, resp)

    @mock.patch('requests.get')
    def test_job_binary_internal_list(self, mget):
        mget.return_value = base.FakeResponse(200, [self.body], 'binaries')

        resp = self.client.job_binary_internals.list()

        self.assertEqual('http://localhost:8386/job-binary-internals',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], jbi.JobBinaryInternal)
        self.assertFields(self.body, resp[0])

    @mock.patch('requests.get')
    def test_job_binary_get(self, mget):
        mget.return_value = base.FakeResponse(200, self.body,
                                              'job_binary_internal')

        resp = self.client.job_binary_internals.get('id')

        self.assertEqual('http://localhost:8386/job-binary-internals/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, jbi.JobBinaryInternal)
        self.assertFields(self.body, resp)

    @mock.patch('requests.delete')
    def test_job_binary_delete(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.job_binary_internals.delete('id')

        self.assertEqual('http://localhost:8386/job-binary-internals/id',
                         mdelete.call_args[0][0])
