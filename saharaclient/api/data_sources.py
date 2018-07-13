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


class DataSources(base.Resource):
    resource_name = 'Data Source'


class DataSourceManagerV1(base.ResourceManager):
    resource_class = DataSources
    version = 1.1

    def create(self, name, description, data_source_type,
               url, credential_user=None, credential_pass=None,
               is_public=None, is_protected=None, s3_credentials=None):
        """Create a Data Source."""

        data = {
            'name': name,
            'description': description,
            'type': data_source_type,
            'url': url,
        }
        credentials = {}
        self._copy_if_defined(credentials,
                              user=credential_user,
                              password=credential_pass)
        credentials = credentials or s3_credentials
        self._copy_if_defined(data, is_public=is_public,
                              is_protected=is_protected,
                              credentials=credentials)

        return self._create('/data-sources', data, 'data_source')

    def list(self, search_opts=None, limit=None, marker=None,
             sort_by=None, reverse=None):
        """Get a list of Data Sources."""
        query = base.get_query_string(search_opts, limit=limit, marker=marker,
                                      sort_by=sort_by, reverse=reverse)
        url = "/data-sources%s" % query
        return self._page(url, 'data_sources', limit)

    def get(self, data_source_id):
        """Get information about a Data Source."""
        return self._get('/data-sources/%s' % data_source_id, 'data_source')

    def delete(self, data_source_id):
        """Delete a Data Source."""
        self._delete('/data-sources/%s' % data_source_id)

    def update(self, data_source_id, update_data):
        """Update a Data Source.

        :param dict update_data: dict that contains fields that should be
                                 updated with new values.

        Fields that can be updated:

        * name
        * description
        * type
        * url
        * is_public
        * is_protected
        * credentials - dict with the keys `user` and `password` for data
          source in Swift, or with the keys `accesskey`, `secretkey`,
          `endpoint`, `ssl`, and `bucket_in_path` for data source in S3
        """

        if self.version >= 2:
            UPDATE_FUNC = self._patch
        else:
            UPDATE_FUNC = self._update

        return UPDATE_FUNC('/data-sources/%s' % data_source_id,
                           update_data)


class DataSourceManagerV2(DataSourceManagerV1):
    version = 2

# NOTE(jfreud): keep this around for backwards compatibility
DataSourceManager = DataSourceManagerV1
