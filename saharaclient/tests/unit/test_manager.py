# Copyright (c) 2015 Mirantis Inc.
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

from saharaclient.api import base
from saharaclient.tests.unit import base as test_base


class ManagerTest(test_base.BaseTestCase):

    def setUp(self):
        super(ManagerTest, self).setUp()
        self.man = test_base.TestManager(self.client)

    def test_find(self):
        self.man.list = mock.MagicMock(
            return_value=[mock.Mock(test='foo'),
                          mock.Mock(test='bar')]
        )

        self.assertEqual(2, len(self.man.find()))
        self.assertEqual(1, len(self.man.find(test='foo')))
        self.assertEqual(0, len(self.man.find(test='baz')))

    def test_find_unique(self):
        expected = mock.Mock(test='foo')
        self.man.list = mock.MagicMock(
            return_value=[expected,
                          mock.Mock(test='bar')]
        )

        ex = self.assertRaises(base.APIException,
                               self.man.find_unique, test='baz')
        self.assertEqual(404, ex.error_code)
        ex = self.assertRaises(base.APIException, self.man.find_unique)
        self.assertEqual(409, ex.error_code)
        self.assertEqual(expected, self.man.find_unique(test='foo'))
