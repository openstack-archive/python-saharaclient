# Copyright (c) 2014 Red Hat Inc.
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

import saharaclient.api.client as client
from saharaclient.tests.integration.configs import config as cfg
from swiftclient import client as swift_client

cfg = cfg.ITConfig()
common = cfg.common_config


class Utils(object):
    def __init__(self):
        self.client = client.Client(username=common['OS_USERNAME'],
                                    api_key=common['OS_PASSWORD'],
                                    auth_url=common['OS_AUTH_URL'],
                                    project_name=common['OS_PROJECT_NAME'])


class SwiftUtils(object):
    def __init__(self):
        self.client = swift_client.Connection(
            authurl=common['OS_AUTH_URL'],
            user=common['OS_USERNAME'],
            key=common['OS_PASSWORD'],
            tenant_name=common['OS_TENANT_NAME'],
            auth_version=common['SWIFT_AUTH_VERSION'])
