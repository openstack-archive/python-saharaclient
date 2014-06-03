# Copyright (c) 2013 Mirantis Inc.
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
import testtools

from saharaclient.api import httpclient


class ResourceTest(testtools.TestCase):

    @mock.patch('requests.post')
    def test_post_json_content_type(self, mpost):
        client = httpclient.HTTPClient("http://localhost", "token")
        client.post('/test', '{"json":"True"}')

        self.assertEqual(1, mpost.call_count)
        self.assertEqual('application/json',
                         mpost.call_args[1]['headers']["content-type"])

    @mock.patch('requests.put')
    def test_put_json_content_type(self, mput):
        client = httpclient.HTTPClient("http://localhost", "token")
        client.put('/test', '{"json":"True"}')

        self.assertEqual(1, mput.call_count)
        self.assertEqual('application/json',
                         mput.call_args[1]['headers']["content-type"])

    @mock.patch('requests.post')
    def test_post_nonjson_content_type(self, mpost):
        client = httpclient.HTTPClient("http://localhost", "token")
        client.post('/test', 'nonjson', json=False)

        self.assertEqual(1, mpost.call_count)
        self.assertNotIn("content-type", mpost.call_args[1]['headers'])

    @mock.patch('requests.put')
    def test_put_nonjson_content_type(self, mput):
        client = httpclient.HTTPClient("http://localhost", "token")
        client.put('/test', 'nonjson', json=False)

        self.assertEqual(1, mput.call_count)
        self.assertNotIn("content-type", mput.call_args[1]['headers'])
