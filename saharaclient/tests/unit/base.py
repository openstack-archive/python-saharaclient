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

import six
import testtools

from saharaclient.api import base
from saharaclient.api import client

from requests_mock.contrib import fixture


class BaseTestCase(testtools.TestCase):

    URL = 'http://localhost:8386'
    TOKEN = 'token'

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.responses = self.useFixture(fixture.Fixture())
        self.client = client.Client(sahara_url=self.URL,
                                    input_auth_token=self.TOKEN)

    def assertFields(self, body, obj):
        for key, value in six.iteritems(body):
            self.assertEqual(value, getattr(obj, key))


class TestResource(base.Resource):
    resource_name = 'Test Resource'
    defaults = {'description': 'Test Description',
                'extra': "extra"}


class TestManager(base.ResourceManager):
    resource_class = TestResource
