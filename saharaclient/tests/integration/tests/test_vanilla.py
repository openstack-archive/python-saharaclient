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

import testtools

from saharaclient.tests.integration.configs import config as cfg
import saharaclient.tests.integration.tests.full_test_driver as driver

cfg = cfg.ITConfig()
vanilla = cfg.vanilla_config


class ClusterVanilla(driver.FullTestDriver):

    @testtools.skipIf(vanilla.SKIP_ALL_TESTS_FOR_PLUGIN,
                      'All tests for Vanilla plugin were skipped')
    def test_cluster_vanilla(self):
        marker = str(os.getpid())
        ng_templates = [
            {
                "values": {
                    "name": "w-%s" % marker,
                    "flavor_id": "2",
                    "plugin_name": vanilla.PLUGIN_NAME,
                    "hadoop_version": vanilla.HADOOP_VERSION,
                    "node_processes": ["tasktracker", "datanode"],
                    "floating_ip_pool": self.floating_ip_pool
                },
                "count": 1
            },
            {
                "values": {
                    "name": "m-%s" % marker,
                    "flavor_id": "2",
                    "plugin_name": vanilla.PLUGIN_NAME,
                    "hadoop_version": vanilla.HADOOP_VERSION,
                    "node_processes": ["jobtracker", "namenode",
                                       "oozie"],
                    "floating_ip_pool": self.floating_ip_pool
                },
                "count": 1
            }
        ]
        self.drive_full_test(vanilla, ng_templates)
