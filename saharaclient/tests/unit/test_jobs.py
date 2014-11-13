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

from saharaclient.api import jobs
from saharaclient.tests.unit import base

import json


class JobTest(base.BaseTestCase):
    body = {
        'name': 'name',
        'type': 'pig',
        'mains': ['job_binary_id'],
        'libs': [],
        'description': 'descr'
    }

    @mock.patch('requests.post')
    def test_create_job(self, mpost):
        mpost.return_value = base.FakeResponse(202, self.body, 'job')

        resp = self.client.jobs.create(**self.body)

        self.assertEqual('http://localhost:8386/jobs',
                         mpost.call_args[0][0])
        self.assertEqual(self.body, json.loads(mpost.call_args[0][1]))
        self.assertIsInstance(resp, jobs.Job)
        self.assertFields(self.body, resp)

    @mock.patch('requests.get')
    def test_jobs_list(self, mget):
        mget.return_value = base.FakeResponse(200, [self.body], 'jobs')

        resp = self.client.jobs.list()

        self.assertEqual('http://localhost:8386/jobs',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], jobs.Job)
        self.assertFields(self.body, resp[0])

    @mock.patch('requests.get')
    def test_jobs_get(self, mget):
        mget.return_value = base.FakeResponse(200, self.body, 'job')

        resp = self.client.jobs.get('id')

        self.assertEqual('http://localhost:8386/jobs/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, jobs.Job)
        self.assertFields(self.body, resp)

    @mock.patch('requests.get')
    def test_jobs_get_configs(self, mget):
        response = {
            "job_config": {
                "args": [],
                "configs": []
            }
        }

        mget.return_value = base.FakeResponse(200, response)

        resp = self.client.jobs.get_configs('Pig')

        self.assertEqual('http://localhost:8386/jobs/config-hints/Pig',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, jobs.Job)
        self.assertFields(response, resp)

    @mock.patch('requests.delete')
    def test_jobs_delete(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.jobs.delete('id')

        self.assertEqual('http://localhost:8386/jobs/id',
                         mdelete.call_args[0][0])
