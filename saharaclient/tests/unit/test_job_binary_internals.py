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

import json

from saharaclient.api import job_binary_internals as jbi
from saharaclient.tests.unit import base


class JobBinaryInternalTest(base.BaseTestCase):
    body = {
        'name': 'name',
        'datasize': '123',
        'id': 'id'
    }

    def test_create_job_binary_internal(self):
        url = self.URL + '/job-binary-internals/name'
        self.responses.put(url, status_code=202,
                           json={'job_binary_internal': self.body})

        resp = self.client.job_binary_internals.create('name', 'data')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual('data', self.responses.last_request.body)
        self.assertIsInstance(resp, jbi.JobBinaryInternal)
        self.assertFields(self.body, resp)

    def test_job_binary_internal_list(self):
        url = self.URL + '/job-binary-internals'
        self.responses.get(url, json={'binaries': [self.body]})

        resp = self.client.job_binary_internals.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], jbi.JobBinaryInternal)
        self.assertFields(self.body, resp[0])

    def test_job_binary_get(self):
        url = self.URL + '/job-binary-internals/id'
        self.responses.get(url, json={'job_binary_internal': self.body})

        resp = self.client.job_binary_internals.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, jbi.JobBinaryInternal)
        self.assertFields(self.body, resp)

    def test_job_binary_delete(self):
        url = self.URL + '/job-binary-internals/id'
        self.responses.delete(url, status_code=204)

        self.client.job_binary_internals.delete('id')

        self.assertEqual(url, self.responses.last_request.url)

    def test_job_binary_update(self):
        url = self.URL + '/job-binary-internals/id'

        update_body = {
            'name': 'new_name'
        }

        self.responses.patch(url, status_code=202, json=update_body)

        resp = self.client.job_binary_internals.update('id', name='new_name')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, jbi.JobBinaryInternal)
        self.assertEqual(update_body,
                         json.loads(self.responses.last_request.body))
