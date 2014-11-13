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

from saharaclient.api import job_binaries as jb
from saharaclient.tests.unit import base

import json


class JobBinaryTest(base.BaseTestCase):
    body = {
        'name': 'name',
        'url': 'url',
        'description': 'descr',
        'extra': {
            'user': 'user',
            'password': '123'
        }
    }

    @mock.patch('requests.post')
    def test_create_job_binary(self, mpost):
        mpost.return_value = base.FakeResponse(202, self.body, 'job_binary')

        resp = self.client.job_binaries.create(**self.body)

        self.assertEqual('http://localhost:8386/job-binaries',
                         mpost.call_args[0][0])
        self.assertEqual(self.body, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, jb.JobBinaries)
        self.assertFields(self.body, resp)

    @mock.patch('requests.get')
    def test_job_binary_list(self, mget):
        mget.return_value = base.FakeResponse(200, [self.body], 'binaries')

        resp = self.client.job_binaries.list()

        self.assertEqual('http://localhost:8386/job-binaries',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], jb.JobBinaries)
        self.assertFields(self.body, resp[0])

    @mock.patch('requests.get')
    def test_job_binary_get(self, mget):
        mget.return_value = base.FakeResponse(200, self.body, 'job_binary')

        resp = self.client.job_binaries.get('id')

        self.assertEqual('http://localhost:8386/job-binaries/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, jb.JobBinaries)
        self.assertFields(self.body, resp)

    @mock.patch('requests.delete')
    def test_job_binary_delete(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.job_binaries.delete('id')

        self.assertEqual('http://localhost:8386/job-binaries/id',
                         mdelete.call_args[0][0])

    @mock.patch('requests.get')
    def test_job_binary_get_file(self, mget):
        mget.return_value = base.FakeResponse(200, 'data')

        resp = self.client.job_binaries.get_file('id')

        self.assertEqual('http://localhost:8386/job-binaries/id/data',
                         mget.call_args[0][0])
        self.assertEqual('data', resp)
