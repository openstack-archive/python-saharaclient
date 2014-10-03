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

import os
import time

import saharaclient.api.base as api_base
from saharaclient.tests.integration.configs import config as cfg
import saharaclient.tests.integration.tests.base as base

from neutronclient.v2_0 import client as neutron_client
import novaclient.exceptions
from novaclient.v1_1 import client as nova_client

cfg = cfg.ITConfig()

common = cfg.common_config

PROP_DESCR = '_sahara_description'
PROP_USERNAME = '_sahara_username'
PROP_TAG = '_sahara_tag_'


class ClusterTest(base.ITestBase):
    def setUp(self):
        super(ClusterTest, self).setUp()

        self.cluster = None
        self.cluster_template = None
        self.image = None
        self.created_key = False
        self.node_group_templates = []

        self.nova = nova_client.Client(
            username=common.OS_USERNAME,
            api_key=common.OS_PASSWORD,
            project_id=common.OS_PROJECT_NAME,
            auth_url=common.OS_AUTH_URL)

        # Get the network ids for the managmenet network and the
        # floating ip pool if we are using neutron
        if common.NEUTRON_ENABLED:
            self.neutron = neutron_client.Client(
                username=common.OS_USERNAME,
                password=common.OS_PASSWORD,
                tenant_name=common.OS_TENANT_NAME,
                auth_url=common.OS_AUTH_URL)
            self.floating_ip_pool = self.find_network_id(
                common.FLOATING_IP_POOL)
            self.neutron_mgmt_net = self.find_network_id(
                common.INTERNAL_NEUTRON_NETWORK)
        else:
            self.neutron = None
            self.floating_ip_pool = common.FLOATING_IP_POOL
            self.neutron_mgmt_net = None

    def find_network_id(self, netname):
        try:
            net = self.neutron.list_networks(name=netname)
            net_id = net['networks'][0]['id']
            return net_id
        except IndexError:
            raise Exception(
                '\nNetwork \'%s\' not found in network list. '
                'Please make sure you specified right network name.' % netname)

    def tearDown(self):
        super(ClusterTest, self).tearDown()
        if self.created_key:
            self.nova.keypairs.delete(self.keypair)

    def init_keypair(self):
        # Figure out what keypair to use, and track whether
        # or not we created it for this test
        self.keypair = common.USER_KEYPAIR_ID
        if not self.keypair:
            self.keypair = 'key%s' % os.getpid()
        self.created_key = False
        try:
            self.nova.keypairs.get(self.keypair)
        except novaclient.exceptions.NotFound:
            self.nova.keypairs.create(self.keypair)
            self.created_key = True

    def find_image_id(self, config):

        basic_msg = '\nImage with %s "%s" was found in image list but it was '
        'possibly not registered for Sahara. Please, make sure '
        'image was correctly registered.'

        long_msg = '\nNone of parameters of image (ID, name, tag)'
        ' was specified in configuration file of '
        'integration tests. That is why there was '
        'attempt to choose image by tag '
        '"sahara_i_tests" and image with such tag '
        'was found in image list but it was possibly '
        'not registered for Sahara. Please, make '
        'sure image was correctly registered.'

        images = self.nova.images.list()

        def try_get_image_id_and_ssh_username(image, msg):
            try:
                if not config.SSH_USERNAME:
                    return image.id, image.metadata[PROP_USERNAME]
                return image.id, config.SSH_USERNAME
            except KeyError as e:
                print(msg)
                raise(e)

        # If config.IMAGE_ID is not None then find corresponding image
        # and return its ID and username. If image not found then handle error
        if config.IMAGE_ID:
            for image in images:
                if image.id == config.IMAGE_ID:
                    return try_get_image_id_and_ssh_username(
                        image,
                        basic_msg % ('ID', image.id))
            self.fail(
                '\n\nImage with ID "%s" not found in image list. '
                'Please, make sure you specified right image ID.\n' %
                config.IMAGE_ID)

        # If config.IMAGE_NAME is not None then find corresponding image
        # and return its ID and username. If image not found then handle error
        if config.IMAGE_NAME:
            for image in images:
                if image.name == config.IMAGE_NAME:
                    return try_get_image_id_and_ssh_username(
                        image,
                        basic_msg % ('name', config.IMAGE_NAME))
            self.fail(
                '\n\nImage with name "%s" not found in image list. Please, '
                'make sure you specified right image name.\n' %
                config.IMAGE_NAME)

        # If config.IMAGE_TAG is not None then find corresponding image
        # and return its ID and username. If image not found then handle error
        if config.IMAGE_TAG:
            for image in images:
                if (image.metadata.get(PROP_TAG + '%s'
                                       % config.IMAGE_TAG)) and (
                                           image.metadata.get(PROP_TAG + (
                                               '%s' % config.PLUGIN_NAME))):
                    return try_get_image_id_and_ssh_username(
                        image,
                        basic_msg % ('tag', config.IMAGE_TAG))
            self.fail(
                '\n\nImage with tag "%s" not found in list of registered '
                'images for Sahara. Please, make sure tag "%s" was added to '
                'image and image was correctly registered.\n' %
                (config.IMAGE_TAG, config.IMAGE_TAG))

        # If config.IMAGE_ID, config.IMAGE_NAME and
        # config.IMAGE_TAG are None then image is chosen
        # by tag "sahara_i_tests". If image has tag "sahara_i_tests"
        # (at the same time image ID, image name and image tag were not
        # specified in configuration file of integration tests) then return
        # its ID and username. Found image will be chosen as image for tests.
        # If image with tag "sahara_i_tests" not found then handle error
        for image in images:
            if (image.metadata.get(PROP_TAG + 'sahara_i_tests')) and (
                    image.metadata.get(PROP_TAG + (
                                       '%s' % config.PLUGIN_NAME))):
                return try_get_image_id_and_ssh_username(image, long_msg)
        self.fail(
            '\n\nNone of parameters of image (ID, name, tag) was specified in '
            'configuration file of integration tests. That is why there was '
            'attempt to choose image by tag "sahara_i_tests" but image with '
            'such tag not found in list of registered images for Sahara. '
            'Please, make sure image was correctly registered. Please, '
            'specify one of parameters of image (ID, name or tag) in '
            'configuration file of integration tests.\n'
        )

    def build_cluster(self, config, node_group_info):
        self.init_keypair()
        cluster_name = "%s-%s-%s" % (common.CLUSTER_NAME,
                                     config.PLUGIN_NAME,
                                     config.HADOOP_VERSION.replace(".", ""))
        # Create and tag an image
        image_id, username = self.find_image_id(config)
        self.cli.register_image(image_id, username, cluster_name)
        self.image = self.util.find_image_by_id(image_id)
        self.assertEqual(cluster_name, self.image.description)

        for t in (config.PLUGIN_NAME, config.HADOOP_VERSION):
            self.cli.tag_image(self.image.id, t)
            self.image = self.util.find_image_by_id(self.image.id)
            self.assertIn(t, self.image.tags)

        for ng_info in node_group_info:
            # Create node group templates
            f = self.util.generate_json_file(ng_info["values"])
            self.cli.node_group_template_create(f.name)
            t = self.util.find_node_group_template_by_name(
                ng_info["values"]["name"])
            self.assertIsNotNone(t)
            self.check_dict_elems_in_obj(ng_info["values"], t)
            self.node_group_templates.append(
                {
                    "name": t.name,
                    "node_group_template_id": t.id,
                    "count": ng_info["count"]
                }
            )

        # Create cluster template
        cluster_temp_dict = {"name": cluster_name,
                             "plugin_name": config.PLUGIN_NAME,
                             "hadoop_version": config.HADOOP_VERSION,
                             "node_groups": self.node_group_templates}

        f = self.util.generate_json_file(cluster_temp_dict)
        self.cli.cluster_template_create(f.name)
        self.cluster_template = self.util.find_cluster_template_by_name(
            cluster_name)
        self.assertIsNotNone(self.cluster_template)
        self.check_dict_elems_in_obj(cluster_temp_dict,
                                     self.cluster_template,
                                     exclude=['node_groups'])
        for idx in range(len(self.node_group_templates)):
            self.check_dict_is_subset(self.node_group_templates[idx],
                                      self.cluster_template.node_groups[idx])

        # Launch it
        cluster_dict = {"name": self.cluster_template.name,
                        "cluster_template_id": self.cluster_template.id,
                        "hadoop_version": config.HADOOP_VERSION,
                        "default_image_id": self.image.id,
                        "plugin_name": config.PLUGIN_NAME,
                        "user_keypair_id": self.keypair,
                        "neutron_management_network": self.neutron_mgmt_net}

        f = self.util.generate_json_file(cluster_dict)
        self.cli.cluster_create(f.name)
        self.cluster = self.util.find_cluster_by_name(
            self.cluster_template.name)
        self.assertIsNotNone(self.cluster)
        self.check_dict_elems_in_obj(cluster_dict, self.cluster)

    def launch_cluster_or_use_existing(self, config, ng_templates):
        # If existing cluster is set, find it and set self.cluster.
        skip_teardown = config.SKIP_CLUSTER_TEARDOWN
        if config.EXISTING_CLUSTER_ID:
            self.cluster = self.util.find_cluster_by_id(
                config.EXISTING_CLUSTER_ID)
        elif config.EXISTING_CLUSTER_NAME:
            self.cluster = self.util.find_cluster_by_name(
                config.EXISTING_CLUSTER_NAME)
        if self.cluster:
            # Always skip teardown if we used an existing cluster
            skip_teardown = True
            status = self.util.poll_cluster_state(self.cluster.id)
            self.assertEqual('Active', status)
        else:
            try:
                self.build_cluster(config, ng_templates)
                status = self.util.poll_cluster_state(self.cluster.id)
                self.assertEqual('Active', status)
            except Exception as e:
                if not skip_teardown:
                    self.teardown_via_client()
                raise(e)
            # A delay here seems necessary to make sure Oozie is active
            time.sleep(common.DELAY_AFTER_ACTIVE * 60)
        return skip_teardown

    def teardown_cluster(self):
        if self.cluster:
            self.cli.cluster_delete(self.cluster.id)
            self.assertRaises(api_base.APIException,
                              self.util.find_cluster_by_id,
                              self.cluster.id)
            self.cluster = None

        if self.cluster_template:
            self.cli.cluster_template_delete(self.cluster_template.id)
            self.assertRaises(api_base.APIException,
                              self.util.find_cluster_template_by_id,
                              self.cluster_template.id)
            self.cluster_template = None

        for ng in self.node_group_templates:
            self.cli.node_group_template_delete(ng["node_group_template_id"])
            self.assertRaises(api_base.APIException,
                              self.util.find_node_group_template_by_id,
                              ng["node_group_template_id"])
        self.node_group_templates = []

        if self.image:
            # After we unregister the image, the description should
            # be None
            self.cli.unregister_image(self.image.id)
            self.image = self.util.find_image_by_id(self.image.id)
            self.assertIsNone(self.image.description)

    def teardown_via_client(self):
        # This is a last attempt to clean up, not part of the test.
        # Try the cleanup and exit if something goes wrong.
        try:
            if self.cluster:
                self.util.client.clusters.delete(self.cluster.id)
                self.cluster = None
            if self.cluster_template:
                self.util.client.cluster_templates.delete(
                    self.cluster_template.id)
                self.cluster_template = None
            if self.worker:
                self.util.client.node_group_templates.delete(self.worker.id)
                self.worker = None
            if self.master:
                self.util.client.node_group_templates.delete(self.master.id)
                self.master = None
            if self.image:
                self.util.client.images.unregister_image(self.image.id)
                self.image = None
        except Exception:
            pass
