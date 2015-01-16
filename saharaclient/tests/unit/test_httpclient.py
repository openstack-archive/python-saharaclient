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

from requests_mock.contrib import fixture
import testtools

from saharaclient.api import httpclient


class ResourceTest(testtools.TestCase):

    URL = 'http://localhost'
    TOKEN = 'token'

    def setUp(self):
        super(ResourceTest, self).setUp()
        self.responses = self.useFixture(fixture.Fixture())

    def test_post_json_content_type(self):
        m = self.responses.post(self.URL + '/test')

        client = httpclient.HTTPClient(self.URL, self.TOKEN)
        client.post('/test', '{"json":"True"}')

        self.assertEqual(1, m.call_count)
        self.assertEqual('application/json',
                         m.last_request.headers['content-type'])

    def test_put_json_content_type(self):
        m = self.responses.put(self.URL + '/test')

        client = httpclient.HTTPClient(self.URL, self.TOKEN)
        client.put('/test', '{"json":"True"}')

        self.assertEqual(1, m.call_count)
        self.assertEqual('application/json',
                         m.last_request.headers['content-type'])

    def test_post_nonjson_content_type(self):
        m = self.responses.post(self.URL + '/test')

        client = httpclient.HTTPClient(self.URL, self.TOKEN)
        client.post('/test', 'nonjson', json=False)

        self.assertEqual(1, m.call_count)
        self.assertNotIn("content-type", m.last_request.headers)

    def test_put_nonjson_content_type(self):
        m = self.responses.put(self.URL + '/test')

        client = httpclient.HTTPClient(self.URL, self.TOKEN)
        client.put('/test', 'nonjson', json=False)

        self.assertEqual(1, m.call_count)
        self.assertNotIn("content-type", m.last_request.headers)
