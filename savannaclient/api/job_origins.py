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


class JobOrigins(base.Resource):
    resource_name = 'JobOrigin'


class JobOriginsManager(base.ResourceManager):
    resource_class = JobOrigins

    def list(self):
        return self._list('/job-origins', "job_origins")

    def delete(self, job_origin_id):
        return self._delete('/job-origins/%s' % job_origin_id)

    def get(self, job_origin_id):
        return self._get('/job-origins/%s' % job_origin_id)

    def create(self, name, description, storage_type, url, credentials):
        data = {
            'name': name,
            'description': description,
            'storage_type': storage_type,
            'url': url,
            'credentials': credentials
        }

        self._create('/job-origins', data)
