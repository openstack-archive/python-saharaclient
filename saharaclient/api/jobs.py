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
    NotUpdated = base.NotUpdated()

    def create(self, name, type, mains=None, libs=None, description=None,
               interface=None, is_public=None, is_protected=None):
        """Create a Job."""
        data = {
            'name': name,
            'type': type
        }

        self._copy_if_defined(data, description=description, mains=mains,
                              libs=libs, interface=interface,
                              is_public=is_public, is_protected=is_protected)

        return self._create('/jobs', data, 'job')

    def list(self, search_opts=None):
        """Get a list of Jobs."""
        query = base.get_query_string(search_opts)
        return self._list('/jobs%s' % query, 'jobs')

    def get(self, job_id):
        """Get information about a Job"""
        return self._get('/jobs/%s' % job_id, 'job')

    def get_configs(self, job_type):
        """Get config hints for a specified Job type."""
        return self._get('/jobs/config-hints/%s' % job_type)

    def delete(self, job_id):
        """Delete a Job"""
        self._delete('/jobs/%s' % job_id)

    def update(self, job_id, name=NotUpdated, description=NotUpdated,
               is_public=NotUpdated, is_protected=NotUpdated):
        """Update a Job."""

        data = {}
        self._copy_if_updated(data, name=name, description=description,
                              is_public=is_public, is_protected=is_protected)

        return self._patch('/jobs/%s' % job_id, data)
