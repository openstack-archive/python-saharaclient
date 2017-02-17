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

from six.moves.urllib import parse as urlparse

from saharaclient.api import base


class JobBinaryInternal(base.Resource):
    resource_name = 'JobBinaryInternal'


class JobBinaryInternalsManager(base.ResourceManager):
    resource_class = JobBinaryInternal
    NotUpdated = base.NotUpdated()

    def create(self, name, data):
        """Create a Job Binary Internal.

        :param str data: raw data of script text
        """
        return self._update('/job-binary-internals/%s' %
                            urlparse.quote(name.encode('utf-8')), data,
                            'job_binary_internal', dump_json=False)

    def list(self, search_opts=None, limit=None, marker=None,
             sort_by=None, reverse=None):
        """Get a list of Job Binary Internals."""
        query = base.get_query_string(search_opts, limit=limit, marker=marker,
                                      sort_by=sort_by, reverse=reverse)
        url = "/job-binary-internals%s" % query
        return self._page(url, 'binaries', limit)

    def get(self, job_binary_id):
        """Get information about a Job Binary Internal."""
        return self._get('/job-binary-internals/%s' % job_binary_id,
                         'job_binary_internal')

    def delete(self, job_binary_id):
        """Delete a Job Binary Internal."""
        self._delete('/job-binary-internals/%s' % job_binary_id)

    def update(self, job_binary_id, name=NotUpdated, is_public=NotUpdated,
               is_protected=NotUpdated):
        """Update a Job Binary Internal."""

        data = {}
        self._copy_if_updated(data, name=name, is_public=is_public,
                              is_protected=is_protected)

        return self._patch('/job-binary-internals/%s' % job_binary_id, data)
