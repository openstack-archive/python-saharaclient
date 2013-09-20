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


class JobBinariesManager(base.ResourceManager):
    resource_class = JobBinaries

    def list(self):
        return self._list('/job-binaries', "binaries")

    def delete(self, job_binary_id):
        return self._delete('/job-binaries/%s' % job_binary_id)

    def create(self, name, url, description=None):
        data = {
            'name': name,
            'url': url,
        }

        self._copy_if_defined(data, description=description)

        return self._create("/job-binaries", data, "job_binary")
