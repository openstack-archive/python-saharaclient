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

from savannaclient.api import base


class JobExecutions(base.Resource):
    resource_name = 'JobExecution'


class JobExecutionsManager(base.ResourceManager):
    resource_class = JobExecutions

    def list(self):
        return self._list('/job-executions', "job_executions")

    def get(self, job_execution_id):
        return self._get('/job-executions/%s' % job_execution_id)

    def cancel(self, job_execution_id):
        return self._get('/job-executions/%s/cancel' % job_execution_id)

    def delete(self, job_execution_id):
        return self._delete('/job-executions/%s' % job_execution_id)

    def execute(self, job_id, input_id, output_id, cluster_id):
        data = {
            'input_id': input_id,
            'output_id': output_id,
            'cluster_id': cluster_id,
        }

        return self._create('/jobs/%s/execute' % job_id, data, "job_execution")
