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


class JobBinaries(base.Resource):
    resource_name = 'Job Binary'


class JobBinariesManager(base.ResourceManager):
    resource_class = JobBinaries

    def create(self, name, url, description, extra, is_public=None,
               is_protected=None):
        data = {
            "name": name,
            "url": url,
            "description": description,
            "extra": extra
        }

        self._copy_if_defined(data, is_public=is_public,
                              is_protected=is_protected)

        return self._create('/job-binaries', data, 'job_binary')

    def list(self, search_opts=None):
        query = base.get_query_string(search_opts)
        return self._list('/job-binaries%s' % query, 'binaries')

    def get(self, job_binary_id):
        return self._get('/job-binaries/%s' % job_binary_id, 'job_binary')

    def delete(self, job_binary_id):
        self._delete('/job-binaries/%s' % job_binary_id)

    def get_file(self, job_binary_id):
        resp = self.api.get('/job-binaries/%s/data' % job_binary_id)

        if resp.status_code != 200:
            self._raise_api_exception(resp)
        return resp.content

    def update(self, job_binary_id, data):
        return self._update(
            '/job-binaries/%s' % job_binary_id, data, 'job_binary')
