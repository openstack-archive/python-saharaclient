# Copyright (c) 2015 Red Hat Inc.
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

from saharaclient.api import job_types as jt
from saharaclient.tests.unit import base


class JobTypesTest(base.BaseTestCase):
    body = {
        "name": "Hive",
        "plugins": [
            {
                "description": "The Apache Vanilla plugin.",
                "name": "vanilla",
                "title": "Vanilla Apache Hadoop",
                "versions": {
                    "1.2.1": {}
                }
            },
            {
                "description": "The Hortonworks Sahara plugin.",
                "name": "hdp",
                "title": "Hortonworks Data Platform",
                "versions": {
                    "1.3.2": {},
                    "2.0.6": {}
                }
            }
        ]
    }

    def test_job_types_list(self):
        url = self.URL + '/job-types'
        self.responses.get(url, json={'job_types': [self.body]})

        resp = self.client.job_types.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], jt.JobType)
        self.assertFields(self.body, resp[0])
