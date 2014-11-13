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

from saharaclient.api import job_executions as je
from saharaclient.tests.unit import base

import json


class JobExecutionTest(base.BaseTestCase):
    body = {
        'job_id': 'job_id',
        'cluster_id': 'cluster_id',
        'configs': {},
        'input_id': None,
        'output_id': None
    }
    response = {
        'cluster_id': 'cluster_id',
        'job_configs': {},
    }

    @mock.patch('requests.post')
    def test_create_job_execution_with_io(self, mpost):
        body = self.body.copy()
        body.update({'input_id': 'input_id', 'output_id': 'output_id'})
        response = self.response.copy()
        response.update({'input_id': 'input_id', 'output_id': 'output_id'})

        mpost.return_value = base.FakeResponse(202, response,
                                               'job_execution')

        resp = self.client.job_executions.create(**body)

        self.assertEqual('http://localhost:8386/jobs/job_id/execute',
                         mpost.call_args[0][0])
        self.assertEqual(response, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, je.JobExecution)
        self.assertFields(response, resp)

    @mock.patch('requests.post')
    def test_create_job_execution_without_io(self, mpost):
        mpost.return_value = base.FakeResponse(202, self.response,
                                               'job_execution')

        resp = self.client.job_executions.create(**self.body)

        self.assertEqual('http://localhost:8386/jobs/job_id/execute',
                         mpost.call_args[0][0])
        self.assertEqual(self.response, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, je.JobExecution)
        self.assertFields(self.response, resp)

    @mock.patch('requests.get')
    def test_job_executions_list(self, mget):
        mget.return_value = base.FakeResponse(200, [self.response],
                                              'job_executions')

        resp = self.client.job_executions.list()

        self.assertEqual('http://localhost:8386/job-executions',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], je.JobExecution)
        self.assertFields(self.response, resp[0])

    @mock.patch('requests.get')
    def test_job_executions_get(self, mget):
        mget.return_value = base.FakeResponse(200, self.response,
                                              'job_execution')

        resp = self.client.job_executions.get('id')

        self.assertEqual('http://localhost:8386/job-executions/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, je.JobExecution)
        self.assertFields(self.response, resp)

    @mock.patch('requests.delete')
    def test_job_executions_delete(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.job_executions.delete('id')

        self.assertEqual('http://localhost:8386/job-executions/id',
                         mdelete.call_args[0][0])
