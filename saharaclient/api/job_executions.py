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
    NotUpdated = base.NotUpdated()

    def list(self, search_opts=None, marker=None, limit=None,
             sort_by=None, reverse=None):
        """Get a list of Job Executions."""
        query = base.get_query_string(search_opts, limit=limit, marker=marker,
                                      sort_by=sort_by, reverse=reverse)
        url = "/job-executions%s" % query
        return self._page(url, 'job_executions', limit)

    def get(self, obj_id):
        """Get information about a Job Execution."""
        return self._get('/job-executions/%s' % obj_id, 'job_execution')

    def delete(self, obj_id):
        """Delete a Job Execution."""
        self._delete('/job-executions/%s' % obj_id)

    def create(self, job_id, cluster_id, input_id=None,
               output_id=None, configs=None, interface=None, is_public=None,
               is_protected=None):
        """Launch a Job."""

        url = "/jobs/%s/execute" % job_id
        data = {
            "cluster_id": cluster_id,
        }

        self._copy_if_defined(data, input_id=input_id, output_id=output_id,
                              job_configs=configs, interface=interface,
                              is_public=is_public, is_protected=is_protected)

        return self._create(url, data, 'job_execution')

    def update(self, obj_id, is_public=NotUpdated, is_protected=NotUpdated):
        """Update a Job Execution."""

        data = {}
        self._copy_if_updated(data, is_public=is_public,
                              is_protected=is_protected)
        return self._patch('/job-executions/%s' % obj_id, data)
