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


class DataSourceManager(base.ResourceManager):
    resource_class = DataSources

    def create(self, name, description, data_source_type,
               url, credential_user=None, credential_pass=None,
               is_public=None, is_protected=None):
        data = {
            'name': name,
            'description': description,
            'type': data_source_type,
            'url': url,
            'credentials': {}
        }
        self._copy_if_defined(data['credentials'],
                              user=credential_user,
                              password=credential_pass)

        self._copy_if_defined(data, is_public=is_public,
                              is_protected=is_protected)

        return self._create('/data-sources', data, 'data_source')

    def list(self, search_opts=None):
        query = base.get_query_string(search_opts)
        return self._list('/data-sources%s' % query, 'data_sources')

    def get(self, data_source_id):
        return self._get('/data-sources/%s' % data_source_id, 'data_source')

    def delete(self, data_source_id):
        self._delete('/data-sources/%s' % data_source_id)

    def update(self, data_source_id, update_data):
        return self._update('/data-sources/%s' % data_source_id,
                            update_data)
