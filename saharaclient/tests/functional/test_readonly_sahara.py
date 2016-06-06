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

from saharaclient.tests.functional import base


class SimpleReadOnlySaharaClientTest(base.ClientTestBase):
    """Basic, read-only tests for Sahara CLI client.

    Checks return values and output of read-only commands.
    These tests do not presume any content, nor do they create
    their own. They only verify the structure of output if present.
    """

    def test_openstack_cluster_list(self):
        result = self.openstack('dataprocessing cluster list')
        clusters = self.parser.listing(result)
        self.assertTableStruct(clusters, [
            'Name',
            'Id',
            'Plugin name',
            'Plugin version',
            'Status'
        ])

    def test_openstack_cluster_template_list(self):
        result = self.openstack('dataprocessing cluster template list')
        templates = self.parser.listing(result)
        self.assertTableStruct(templates, [
            'Name',
            'Id',
            'Plugin name',
            'Plugin version'
        ])

    def test_openstack_image_list(self):
        result = self.openstack('dataprocessing image list')
        images = self.parser.listing(result)
        self.assertTableStruct(images, [
            'Name',
            'Id',
            'Username',
            'Tags'
        ])

    def test_openstack_job_binary_list(self):
        result = self.openstack('dataprocessing job binary list')
        job_binary = self.parser.listing(result)
        self.assertTableStruct(job_binary, [
            'name',
            'url'
        ])

    def test_openstack_job_template_list(self):
        result = self.openstack('dataprocessing job template list')
        job_template = self.parser.listing(result)
        self.assertTableStruct(job_template, [
            'name',
            'type'
        ])

    def test_openstack_data_source_list(self):
        result = self.openstack('dataprocessing data source list')
        data_source = self.parser.listing(result)
        self.assertTableStruct(data_source, [
            'name',
            'type',
            'url'
        ])

    def test_openstack_job_type_list(self):
        result = self.openstack('dataprocessing job type list')
        job_type = self.parser.listing(result)
        self.assertTableStruct(job_type, [
            'Name',
            'Plugins'
        ])

    def test_openstack_node_group_template_list(self):
        result = self.openstack('dataprocessing node group template list')
        node_group = self.parser.listing(result)
        self.assertTableStruct(node_group, [
            'Name',
            'Id',
            'Plugin version',
            'Plugin name'
        ])

    def test_openstack_plugin_list(self):
        result = self.openstack('dataprocessing plugin list')
        plugin = self.parser.listing(result)
        self.assertTableStruct(plugin, [
            'Name',
            'Versions'
        ])

    def test_openstack_job_list(self):
        result = self.openstack('dataprocessing job list')
        jobs = self.parser.listing(result)
        self.assertTableStruct(jobs, [
            'id',
            'cluster_id',
            'status'
        ])
