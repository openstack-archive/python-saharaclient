# Copyright (c) 2015 Red Hat Inc.
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


class JobType(base.Resource):
    resource_name = 'JobType'


class JobTypesManager(base.ResourceManager):
    resource_class = JobType

    def list(self, search_opts=None):
        """Get a list of job types supported by plugins."""
        query = base.get_query_string(search_opts)
        return self._list('/job-types%s' % query, 'job_types')
