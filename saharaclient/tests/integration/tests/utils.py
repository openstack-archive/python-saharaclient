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

import json
import six
import tempfile
import time

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

    def find_image_by_id(self, id):
        return self.client.images.get(id)

    def find_cluster_by_id(self, id):
        return self.client.clusters.get(id)

    def find_node_group_template_by_id(self, id):
        return self.client.node_group_templates.get(id)

    def find_cluster_template_by_id(self, id):
        return self.client.cluster_templates.get(id)

    def find_object_by_field(self, val, obj_list, field="name"):
        for obj in obj_list:
            if getattr(obj, field) == val:
                return obj

    def find_node_group_template_by_name(self, name):
        return self.find_object_by_field(
            name,
            self.client.node_group_templates.list())

    def find_cluster_template_by_name(self, name):
        return self.find_object_by_field(name,
                                         self.client.cluster_templates.list())

    def find_cluster_by_name(self, name):
        return self.find_object_by_field(name,
                                         self.client.clusters.list())

    def generate_json_file(self, temp):
        f = tempfile.NamedTemporaryFile(delete=True)
        f.write(json.dumps(temp))
        f.flush()
        return f

    def poll_cluster_state(self, id):
        cluster = self.client.clusters.get(id)
        #TODO(tmckay): this should use timeutils but we need
        #to add it to openstack/common
        timeout = common['CLUSTER_CREATION_TIMEOUT'] * 60
        while str(cluster.status) != 'Active':
            if str(cluster.status) == 'Error' or timeout <= 0:
                break
            time.sleep(10)
            timeout -= 10
            cluster = self.client.clusters.get(id)
        return str(cluster.status)


class SwiftUtils(object):
    def __init__(self):
        self.client = swift_client.Connection(
            authurl=common['OS_AUTH_URL'],
            user=common['OS_USERNAME'],
            key=common['OS_PASSWORD'],
            tenant_name=common['OS_TENANT_NAME'],
            auth_version=common['SWIFT_AUTH_VERSION'])


class AssertionWrappers(object):
    def check_dict_elems_in_obj(self, d, obj, exclude=[]):
        for key, val in six.iteritems(d):
            if key not in exclude:
                self.assertEqual(val, getattr(obj, key))

    def check_dict_is_subset(self, dict1, dict2):
        # There is an assert for this in Python 2.7 but not 2.6
        self.assertTrue(all(
            k in dict2 and dict2[k] == v for k, v in six.iteritems(dict1)))
