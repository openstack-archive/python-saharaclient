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


class Jobs(base.Resource):
    resource_name = 'Job'


class JobsManager(base.ResourceManager):
    resource_class = Jobs

    def list(self):
        return self._list('/jobs', "jobs")

    def delete(self, job_id):
        return self._delete('/jobs/%s' % job_id)

    def get(self, job_id):
        return self._get('/jobs/%s' % job_id)

    def create(self, name, description, job_origin_id,
               job_type, input_type, output_type):
        data = {
            'name': name,
            'description': description,
            'type': job_type,
            'job_origin_id': job_origin_id,
            'input_type': input_type,
            'output_type': output_type
        }

        return self._create('/jobs', data)
