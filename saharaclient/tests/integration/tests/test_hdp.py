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

import testtools

from saharaclient.tests.integration.configs import config as cfg
import saharaclient.tests.integration.tests.full_test_driver as driver

cfg = cfg.ITConfig()
hdp = cfg.hdp_config


class ClusterHDP(driver.FullTestDriver):

    @testtools.skipIf(hdp.SKIP_ALL_TESTS_FOR_PLUGIN,
                      'All tests for Hdp plugin were skipped')
    def test_cluster_hdp(self):
        ng_templates = {}
        self.drive_full_test(hdp, ng_templates)
