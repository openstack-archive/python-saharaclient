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

import saharaclient.tests.integration.tests.cluster as cluster
import saharaclient.tests.integration.tests.edp as edp


class FullTestDriver(edp.EDPTest, cluster.ClusterTest):

    def drive_full_test(self, config, ng_templates):
        # If we get an exception during cluster launch, the cluster has already
        # been cleaned up and we don't have to do anything here
        skip_teardown = self.launch_cluster_or_use_existing(config,
                                                            ng_templates)
        try:
            self.run_edp_jobs(config)
            if not skip_teardown:
                self.teardown_cluster()
        except Exception as e:
            # Oops.  Teardown via CLI is part of the test,
            # but something went wrong early.  Try tear down via the client.
            # TODO(tmckay): use excutils from openstack/common
            import traceback
            traceback.print_exc()
            if not skip_teardown:
                self.teardown_via_client()
            raise(e)
