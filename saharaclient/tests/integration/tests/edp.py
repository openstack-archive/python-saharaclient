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

import saharaclient.api.base as api_base
from saharaclient.tests.integration.configs import config as cfg
import saharaclient.tests.integration.tests.base as base
import saharaclient.tests.integration.tests.utils as utils

cfg = cfg.ITConfig()
common = cfg.common_config


class EDPTest(base.ITestBase):
    def setUp(self):
        super(EDPTest, self).setUp()

        self.swift_utils = utils.SwiftUtils()
        self.path = 'saharaclient/tests/integration/tests/resources/'

        self.job = None
        self.job_template = None
        self.lib_binary = None
        self.main_binary = None
        self.input_source = None
        self.output_source = None

    def tearDown(self):
        super(EDPTest, self).tearDown()
        self.swift_utils.delete_containers()

    def _create_binary(self, marker, info, url):
        # Use the marker value to distinguish the object, but
        # the name must start with a letter and include a file
        # extension.
        binary_name = '%s-%s' % (marker, info['name'])
        self.cli.job_binary_create(binary_name,
                                   url,
                                   username=common.OS_USERNAME,
                                   password=common.OS_PASSWORD)
        binary_obj = self.util.find_job_binary_by_name(binary_name)
        self.assertIsNotNone(binary_obj)
        self.assertEqual(binary_name, binary_obj.name)
        self.assertEqual(url, binary_obj.url)
        return binary_obj

    def _create_swift_binary(self, marker, container, info):
        if not info:
            return None
        self.swift_utils.upload(container, info['name'], info['data'])
        url = 'swift://%s/%s' % (container, info['name'])
        return self._create_binary(marker, info, url)

    def _create_internal_binary(self, marker, info):
        if not info:
            return None, None
        output = self.cli.job_binary_data_create(info['path'])
        id = self.util.find_binary_internal_id(output)
        url = 'internal-db://%s' % id
        return self._create_binary(marker, info, url), id

    def _create_data_source(self, name, url):
        self.cli.data_source_create(name, 'swift', url,
                                    username=common.OS_USERNAME,
                                    password=common.OS_PASSWORD)
        source = self.util.find_data_source_by_name(name)
        self.assertIsNotNone(source)
        return source

    def _binary_info(self, fname, relative_path=""):
        # Binaries need to be named, and the name must include
        # the file extension since Oozie depends on it. So, we
        # just store the filename for the name here.
        info = {'name': fname}
        if common.INTERNAL_JOB_BINARIES:
            # We will use the cli to upload the file by path
            info['path'] = self.path + relative_path + fname
        else:
            # We will upload the binary data to swift
            info['data'] = open(self.path + relative_path + fname).read()
        return info

    def edp_common(self, job_type, lib=None, main=None, configs=None,
                   add_data_sources=True, pass_data_sources_as_args=False,
                   job_interface=None, execution_interface=None):
        # Generate a new marker for this so we can keep containers separate
        # and create some input data
        job_interface = job_interface or []
        execution_interface = execution_interface or {}
        marker = "%s-%s" % (job_type.replace(".", ""), os.getpid())
        container = self.swift_utils.create_container(marker)
        self.swift_utils.generate_input(container, 'input')
        input_url = 'swift://%s.sahara/input' % container
        output_url = 'swift://%s.sahara/output' % container

        # Create binaries
        if common.INTERNAL_JOB_BINARIES:
            (self.lib_binary,
             self.lib_data_id) = self._create_internal_binary(marker, lib)
            (self.main_binary,
             self.main_data_id) = self._create_internal_binary(marker, main)
        else:
            self.lib_data_id = None
            self.main_data_id = None
            self.lib_binary = self._create_swift_binary(marker, container, lib)
            self.main_binary = self._create_swift_binary(marker,
                                                         container, main)

        # Create data sources
        if add_data_sources:
            self.input_source = self._create_data_source('input-%s' % marker,
                                                         input_url)
            self.output_source = self._create_data_source('output-%s' % marker,
                                                          output_url)
        else:
            self.input_source = self.output_source = None

        # Create a job template
        job_template_name = marker
        job_template_dict = {
            "name": job_template_name,
            "type": job_type,
            "mains": [self.main_binary.id] if (self.main_binary and
                                               self.main_binary.id) else [],
            "libs": [self.lib_binary.id] if (self.lib_binary and
                                             self.lib_binary.id) else [],
            "interface": job_interface
        }
        f = self.util.generate_json_file(job_template_dict)
        self.cli.job_template_create(f.name)
        self.job_template = self.util.find_job_template_by_name(
            job_template_name)
        self.assertIsNotNone(self.job_template)
        self.assertEqual(job_template_name, self.job_template.name)
        self.assertEqual(job_type, self.job_template.type)
        if self.lib_binary:
            self.assertEqual(1, len(self.job_template.libs))
            self.assertEqual(self.job_template.libs[0]['id'],
                             self.lib_binary.id)
        if self.main_binary:
            self.assertEqual(1, len(self.job_template.mains))
            self.assertEqual(self.job_template.mains[0]['id'],
                             self.main_binary.id)

        # Launch the job
        if pass_data_sources_as_args:
            args = [input_url, output_url]
        else:
            args = None

        job_dict = {
            "cluster_id": self.cluster.id,
            "input_id": self.input_source and (
                self.input_source.id or None),
            "output_id": self.output_source and (
                self.output_source.id or None),
            "job_configs": {"configs": configs,
                            "args": args},
            "interface": execution_interface
        }
        f = self.util.generate_json_file(job_dict)
        self.cli.job_create(self.job_template.id, f.name)

        # Find the job using the job_template_id
        self.job = self.util.find_job_by_job_template_id(self.job_template.id)
        self.assertIsNotNone(self.job)
        self.assertEqual(self.cluster.id, self.job.cluster_id)

        # poll for status
        status = self.util.poll_job_execution(self.job.id)
        self.assertEqual('SUCCEEDED', status)

        # follow up with a deletion of the stuff we made from a util function
        self.delete_job_objects()

    def pig_edp(self):
        self.edp_common('Pig',
                        lib=self._binary_info('edp-lib.jar'),
                        main=self._binary_info('edp-job.pig'))

    def mapreduce_edp(self):
        configs = {
            "mapred.mapper.class": "org.apache.oozie.example.SampleMapper",
            "mapred.reducer.class": "org.apache.oozie.example.SampleReducer"
        }
        self.edp_common('MapReduce',
                        lib=self._binary_info('edp-mapreduce.jar'),
                        configs=configs)

    def mapreduce_streaming_edp(self):
        configs = {
            "edp.streaming.mapper": "/bin/cat",
            "edp.streaming.reducer": "/usr/bin/wc"
        }
        self.edp_common('MapReduce.Streaming',
                        configs=configs)

    def java_edp(self):
        configs = {
            'fs.swift.service.sahara.password': common.OS_PASSWORD,
            'edp.java.main_class': 'org.openstack.sahara.examples.WordCount'
        }
        job_interface = [{
            "name": "Swift Username",
            "mapping_type": "configs",
            "location": "fs.swift.service.sahara.username",
            "value_type": "string",
            "required": True
        }]
        execution_interface = {"Swift Username": common.OS_USERNAME}
        self.edp_common('Java',
                        lib=self._binary_info('edp-java.jar',
                                              relative_path='edp-java/'),
                        configs=configs,
                        add_data_sources=False,
                        pass_data_sources_as_args=True,
                        job_interface=job_interface,
                        execution_interface=execution_interface)

    def run_edp_jobs(self, config):
        try:
            if not config.SKIP_JAVA_EDP_TEST:
                self.java_edp()
            if not config.SKIP_MAPREDUCE_EDP_TEST:
                self.mapreduce_edp()
            if not config.SKIP_MAPREDUCE_STREAMING_EDP_TEST:
                self.mapreduce_streaming_edp()
            if not config.SKIP_PIG_EDP_TEST:
                self.pig_edp()
        except Exception as e:
            # Something went wrong, try to clean up what might be left
            self.delete_job_objects_via_client()
            raise(e)

    def delete_job_objects(self):
        if self.job:
            self.cli.job_delete(self.job.id)
            self.assertRaises(api_base.APIException,
                              self.util.find_job_by_id,
                              self.job.id)
            self.job = None

        if self.job_template:
            self.cli.job_template_delete(self.job_template.id)
            self.assertRaises(api_base.APIException,
                              self.util.find_job_template_by_id,
                              self.job_template.id)
            self.job_template = None

        if self.lib_binary:
            self.cli.job_binary_delete(self.lib_binary.id)
            self.assertRaises(api_base.APIException,
                              self.util.find_job_binary_by_id,
                              self.lib_binary.id)
            self.lib_binary = None

        if self.lib_data_id:
            self.cli.job_binary_data_delete(self.lib_data_id)
            self.assertRaises(api_base.APIException,
                              self.util.find_binary_internal_by_id,
                              self.lib_data_id)
            self.lib_data_id = None

        if self.main_binary:
            self.cli.job_binary_delete(self.main_binary.id)
            self.assertRaises(api_base.APIException,
                              self.util.find_job_binary_by_id,
                              self.main_binary.id)
            self.main_binary = None

        if self.main_data_id:
            self.cli.job_binary_data_delete(self.main_data_id)
            self.assertRaises(api_base.APIException,
                              self.util.find_binary_internal_by_id,
                              self.main_data_id)
            self.main_data_id = None

        if self.input_source:
            self.cli.data_source_delete(self.input_source.id)
            self.assertRaises(api_base.APIException,
                              self.util.find_data_source_by_id,
                              self.input_source.id)
            self.input_source = None

        if self.output_source:
            self.cli.data_source_delete(self.output_source.id)
            self.assertRaises(api_base.APIException,
                              self.util.find_data_source_by_id,
                              self.output_source.id)
            self.output_source = None

    def delete_job_objects_via_client(self):
        try:
            if self.job:
                self.util.client.job_executions.delete(self.job.id)
                self.job = None
            if self.job_template:
                self.util.client.jobs.delete(self.job_template.id)
                self.job_template = None
            if self.lib_binary:
                self.util.client.job_binaries.delete(self.lib_binary.id)
                self.lib_binary = None
            if self.main_binary:
                self.util.client.job_binaries.delete(self.main_binary.id)
                self.main_binary = None
            if self.input_source:
                self.util.client.data_sources.delete(self.input_source.id)
                self.input_source = None
            if self.output_source:
                self.util.client.data_sources.delete(self.output_source.id)
                self.output_source = None
        except Exception:
            pass
