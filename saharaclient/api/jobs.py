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


class Job(base.Resource):
    resource_name = 'Job'


class JobsManager(base.ResourceManager):
    resource_class = Job

    def create(self, name, type, mains, libs, description, interface=None,
               is_public=None, is_protected=None):
        data = {
            'name': name,
            'type': type,
            'description': description,
            'mains': mains,
            'libs': libs,
        }

        self._copy_if_defined(data, interface=interface, is_public=is_public,
                              is_protected=is_protected)

        return self._create('/jobs', data, 'job')

    def list(self, search_opts=None):
        query = base.get_query_string(search_opts)
        return self._list('/jobs%s' % query, 'jobs')

    def get(self, job_id):
        return self._get('/jobs/%s' % job_id, 'job')

    def get_configs(self, job_type):
        return self._get('/jobs/config-hints/%s' % job_type)

    def delete(self, job_id):
        self._delete('/jobs/%s' % job_id)

    def update(self, job_id, name=None, description=None, is_public=None,
               is_protected=None):

        data = {}
        self._copy_if_defined(data, name=name, description=description,
                              is_public=is_public, is_protected=is_protected)

        return self._patch('/jobs/%s' % job_id, data)
