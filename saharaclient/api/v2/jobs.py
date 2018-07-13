# Copyright (c) 2018 OpenStack Foundation
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


class JobsManagerV2(base.ResourceManager):
    resource_class = Job
    NotUpdated = base.NotUpdated()

    def list(self, search_opts=None, marker=None, limit=None,
             sort_by=None, reverse=None):
        """Get a list of Jobs."""
        query = base.get_query_string(search_opts, limit=limit, marker=marker,
                                      sort_by=sort_by, reverse=reverse)
        url = "/jobs%s" % query
        return self._page(url, 'jobs', limit)

    def get(self, obj_id):
        """Get information about a Job."""
        return self._get('/jobs/%s' % obj_id, 'job')

    def delete(self, obj_id):
        """Delete a Job."""
        self._delete('/jobs/%s' % obj_id)

    def create(self, job_template_id, cluster_id, input_id=None,
               output_id=None, configs=None, interface=None, is_public=None,
               is_protected=None):
        """Launch a Job."""

        data = {
            "cluster_id": cluster_id,
            "job_template_id": job_template_id
        }

        self._copy_if_defined(data, input_id=input_id, output_id=output_id,
                              job_configs=configs, interface=interface,
                              is_public=is_public, is_protected=is_protected)

        return self._create('/jobs', data, 'job')

    def refresh_status(self, obj_id):
        """Refresh Job Status."""
        return self._get(
            '/jobs/%s?refresh_status=True' % obj_id,
            'job'
        )

    def update(self, obj_id, is_public=NotUpdated, is_protected=NotUpdated):
        """Update a Job."""

        data = {}
        self._copy_if_updated(data, is_public=is_public,
                              is_protected=is_protected)
        return self._patch('/jobs/%s' % obj_id, data)
