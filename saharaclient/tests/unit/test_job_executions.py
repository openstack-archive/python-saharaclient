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

from saharaclient.api import job_executions as je
from saharaclient.tests.unit import base

import json


class JobExecutionTest(base.BaseTestCase):
    body = {
        'job_id': 'job_id',
        'cluster_id': 'cluster_id',
        'configs': {},
        'interface': {},
        'input_id': None,
        'output_id': None
    }
    response = {
        'cluster_id': 'cluster_id',
        'job_configs': {}
    }

    update_json = {
        'is_public': True,
        'is_protected': True,
    }

    def test_create_job_execution_with_io(self):
        url = self.URL + '/jobs/job_id/execute'

        body = self.body.copy()
        body.update({'input_id': 'input_id', 'output_id': 'output_id'})
        response = self.response.copy()
        response.update({'input_id': 'input_id', 'output_id': 'output_id'})

        self.responses.post(url, status_code=202,
                            json={'job_execution': response})

        resp = self.client.job_executions.create(**body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(response,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, je.JobExecution)
        self.assertFields(response, resp)

    def test_create_job_execution_without_io(self):
        url = self.URL + '/jobs/job_id/execute'

        self.responses.post(url, status_code=202,
                            json={'job_execution': self.response})

        resp = self.client.job_executions.create(**self.body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(self.response,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, je.JobExecution)
        self.assertFields(self.response, resp)

    def test_job_executions_list(self):
        url = self.URL + '/job-executions'
        self.responses.get(url, json={'job_executions': [self.response]})

        resp = self.client.job_executions.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], je.JobExecution)
        self.assertFields(self.response, resp[0])

    def test_job_executions_get(self):
        url = self.URL + '/job-executions/id'
        self.responses.get(url, json={'job_execution': self.response})

        resp = self.client.job_executions.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, je.JobExecution)
        self.assertFields(self.response, resp)

    def test_job_executions_delete(self):
        url = self.URL + '/job-executions/id'
        self.responses.delete(url, status_code=204)

        self.client.job_executions.delete('id')

        self.assertEqual(url, self.responses.last_request.url)

    def test_job_executions_update(self):
        url = self.URL + '/job-executions/id'
        self.responses.patch(url, status_code=202, json=self.update_json)

        resp = self.client.job_executions.update("id", **self.update_json)
        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, je.JobExecution)
        self.assertEqual(self.update_json,
                         json.loads(self.responses.last_request.body))
