# Copyright (c) 2013 Mirantis Inc.
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

from saharaclient.api import base


class JobExecution(base.Resource):
    resource_name = 'JobExecution'


class JobExecutionsManager(base.ResourceManager):
    resource_class = JobExecution

    def list(self):
        return self._list('/job-executions', 'job_executions')

    def get(self, obj_id):
        return self._get('/job-executions/%s' % obj_id, 'job_execution')

    def delete(self, obj_id):
        self._delete('/job-executions/%s' % obj_id)

    def create(self, job_id, cluster_id, input_id, output_id, configs):
        url = "/jobs/%s/execute" % job_id
        data = {
            "cluster_id": cluster_id,
            "job_configs": configs
        }

        # Leave these out if they are null.  For Java job types they
        # are not part of the schema
        io_ids = (("input_id", input_id),
                  ("output_id", output_id))
        for key, value in io_ids:
            if value is not None:
                data.update({key: value})

        return self._create(url, data, 'job_execution')
