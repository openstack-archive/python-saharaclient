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

from saharaclient.api import job_binaries as jb
from saharaclient.tests.unit import base

from oslo_serialization import jsonutils as json


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

    update_body = {
        'name': 'Updatedname',
        'url': 'Updatedurl',
        'description': 'Updateddescr',
        'extra': {
            'user': 'user',
            'password': 'Updated123'
        }
    }

    def test_create_job_binary(self):
        url = self.URL + '/job-binaries'
        self.responses.post(url, status_code=202,
                            json={'job_binary': self.body})

        resp = self.client.job_binaries.create(**self.body)

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(self.body,
                         json.loads(self.responses.last_request.body))
        self.assertIsInstance(resp, jb.JobBinaries)
        self.assertFields(self.body, resp)

    def test_job_binary_list(self):
        url = self.URL + '/job-binaries'
        self.responses.get(url, json={'binaries': [self.body]})

        resp = self.client.job_binaries.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], jb.JobBinaries)
        self.assertFields(self.body, resp[0])

    def test_job_binary_get(self):
        url = self.URL + '/job-binaries/id'
        self.responses.get(url, json={'job_binary': self.body})

        resp = self.client.job_binaries.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, jb.JobBinaries)
        self.assertFields(self.body, resp)

    def test_job_binary_delete(self):
        url = self.URL + '/job-binaries/id'
        self.responses.delete(url, status_code=204)

        self.client.job_binaries.delete('id')

        self.assertEqual(url, self.responses.last_request.url)

    def test_job_binary_get_file(self):
        url = self.URL + '/job-binaries/id/data'
        self.responses.get(url, text='data')

        resp = self.client.job_binaries.get_file('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(b'data', resp)

    def test_job_binary_update(self):
        url = self.URL + '/job-binaries/id'
        self.responses.put(url,
                           status_code=202,
                           json={'job_binary': self.update_body})

        resp = self.client.job_binaries.update("id", self.update_body)
        self.assertEqual(self.update_body["name"], resp.name)
