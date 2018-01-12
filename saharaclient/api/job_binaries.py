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


class JobBinariesManagerV1(base.ResourceManager):
    resource_class = JobBinaries
    version = 1.1

    def create(self, name, url, description=None, extra=None, is_public=None,
               is_protected=None):
        """Create a Job Binary.

        :param dict extra: authentication info needed for some job binaries,
            containing the keys `user` and `password` for job binary in Swift
            or the keys `accesskey`, `secretkey`, and `endpoint` for job
            binary in S3

        """
        data = {
            "name": name,
            "url": url
        }

        self._copy_if_defined(data, description=description, extra=extra,
                              is_public=is_public, is_protected=is_protected)

        return self._create('/job-binaries', data, 'job_binary')

    def list(self, search_opts=None, limit=None, marker=None,
             sort_by=None, reverse=None):
        """Get a list of Job Binaries."""
        query = base.get_query_string(search_opts, limit=limit, marker=marker,
                                      sort_by=sort_by, reverse=reverse)
        url = "/job-binaries%s" % query
        return self._page(url, 'binaries', limit)

    def get(self, job_binary_id):
        """Get information about a Job Binary."""
        return self._get('/job-binaries/%s' % job_binary_id, 'job_binary')

    def delete(self, job_binary_id):
        """Delete a Job Binary."""
        self._delete('/job-binaries/%s' % job_binary_id)

    def get_file(self, job_binary_id):
        """Download a Job Binary."""
        resp = self.api.get('/job-binaries/%s/data' % job_binary_id)

        if resp.status_code != 200:
            self._raise_api_exception(resp)
        return resp.content

    def update(self, job_binary_id, data):
        """Update Job Binary.

        :param dict data: dict that contains fields that should be updated
                     with new values.

        Fields that can be updated:

        * name
        * description
        * url
        * is_public
        * is_protected
        * extra - dict with the keys `user` and `password` for job binary
          in Swift, or with the keys `accesskey`, `secretkey`, and `endpoint`
          for job binary in S3
        """

        if self.version >= 2:
            UPDATE_FUNC = self._patch
        else:
            UPDATE_FUNC = self._update

        return UPDATE_FUNC(
            '/job-binaries/%s' % job_binary_id, data, 'job_binary')


class JobBinariesManagerV2(JobBinariesManagerV1):
    version = 2


# NOTE(jfreud): keep this around for backwards compatibility
JobBinariesManager = JobBinariesManagerV1
