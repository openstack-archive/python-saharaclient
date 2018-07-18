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

from saharaclient.osc import plugin
from saharaclient.tests.unit import base


class TestDataProcessingPlugin(base.BaseTestCase):

    @mock.patch("saharaclient.api.client.Client")
    def test_make_client(self, p_client):

        instance = mock.Mock()
        instance._api_version = {"data_processing": '1.1'}
        instance.session = 'session'
        instance._region_name = 'region_name'
        instance._cli_options.data_processing_url = 'url'
        instance._interface = 'public'

        plugin.make_client(instance)
        p_client.assert_called_with(session='session',
                                    region_name='region_name',
                                    sahara_url='url',
                                    endpoint_type='public')

    @mock.patch("saharaclient.api.client.ClientV2")
    def test_make_client_v2(self, p_client):

        instance = mock.Mock()
        instance._api_version = {"data_processing": '2'}
        instance.session = 'session'
        instance._region_name = 'region_name'
        instance._cli_options.data_processing_url = 'url'
        instance._interface = 'public'

        plugin.make_client(instance)
        p_client.assert_called_with(session='session',
                                    region_name='region_name',
                                    sahara_url='url',
                                    endpoint_type='public')
