# Copyright (c) 2016 Mirantis Inc.
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

import saharaclient
from saharaclient.api import base as api_base
from saharaclient.tests.unit import base


class BaseTest(base.BaseTestCase):
    def test_get_query_string(self):
        res = api_base.get_query_string(None, limit=None, marker=None)
        self.assertEqual("", res)

        res = api_base.get_query_string(None, limit=4, marker=None)
        self.assertEqual("?limit=4", res)

        res = api_base.get_query_string({'opt1': 2}, limit=None, marker=3)
        self.assertEqual("?marker=3&opt1=2", res)

    def test_module_version(self):
        self.assertTrue(hasattr(saharaclient, '__version__'))
