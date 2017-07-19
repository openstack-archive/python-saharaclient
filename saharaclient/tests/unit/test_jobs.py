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

from saharaclient.api import jobs
from saharaclient.tests.unit import base

from oslo_serialization import jsonutils as json


class JobTest(base.BaseTestCase):
    body = {
        'name': 'name',
        'type': 'pig',
        'mains': ['job_binary_id'],
        'libs': [],
        'description': 'descr',
        'is_public': True,
        'is_protected': False
    }

    def test_create_job(self):
        url = self.URL + '/jobs'
        self.responses.post(url, status_code=202, json={'job': self.body})

        resp = self.client.jobs.create(**self.body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(self.body,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, jobs.Job)
        self.assertFields(self.body, resp)

    def test_jobs_list(self):
        url = self.URL + '/jobs'
        self.responses.get(url, json={'jobs': [self.body]})

        resp = self.client.jobs.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], jobs.Job)
        self.assertFields(self.body, resp[0])

    def test_jobs_get(self):
        url = self.URL + '/jobs/id'
        self.responses.get(url, json={'job': self.body})

        resp = self.client.jobs.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, jobs.Job)
        self.assertFields(self.body, resp)

    def test_jobs_get_configs(self):
        url = self.URL + '/jobs/config-hints/Pig'
        response = {
            "job_config": {
                "args": [],
                "configs": []
            },
            "interface": []
        }
        self.responses.get(url, json=response)

        resp = self.client.jobs.get_configs('Pig')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, jobs.Job)
        self.assertFields(response, resp)

    def test_jobs_delete(self):
        url = self.URL + '/jobs/id'
        self.responses.delete(url, status_code=204)

        self.client.jobs.delete('id')

        self.assertEqual(url, self.responses.last_request.url)

    def test_jobs_update(self):
        url = self.URL + '/jobs/id'

        update_body = {
            'name': 'new_name',
            'description': 'description'
        }

        self.responses.patch(url, status_code=202, json=update_body)

        # check that all parameters will be updated
        resp = self.client.jobs.update('id', name='new_name',
                                       description='description')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, jobs.Job)
        self.assertEqual(update_body,
                         json.loads(self.responses.last_request.body))

        # check that parameters will not be updated
        self.client.jobs.update("id")
        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual({},
                         json.loads(self.responses.last_request.body))

        # check that all parameters will be unset
        unset_json = {
            "name": None, "description": None, "is_public": None,
            "is_protected": None
        }

        self.client.jobs.update("id", **unset_json)
        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(unset_json,
                         json.loads(self.responses.last_request.body))
