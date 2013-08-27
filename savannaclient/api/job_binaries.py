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


class JobBinaries(base.Resource):
    resource_name = 'JobBinary'


class JobExecutionsManager(base.ResourceManager):
    resource_class = JobBinaries

    def list(self):
        return self._list('/job-binaries', "binaries")

    def delete(self, job_binary_id):
        return self._delete('/job-binaries/%s' % job_binary_id)

    def create(self, name, data):
        url = '/job-binaries/%s' % name
        resp = self.api.client.put(url, data)

        if resp.status_code != 202:
            self._raise_api_exception(resp)

        data = resp.json()["resource"]
        return self.resource_class(self, data)
