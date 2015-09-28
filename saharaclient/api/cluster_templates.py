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


class ClusterTemplate(base.Resource):
    resource_name = 'Cluster Template'


class ClusterTemplateManager(base.ResourceManager):
    resource_class = ClusterTemplate

    def create(self, name, plugin_name, hadoop_version, description=None,
               cluster_configs=None, node_groups=None, anti_affinity=None,
               net_id=None, default_image_id=None, use_autoconfig=None,
               shares=None, is_public=None, is_protected=None):

        data = {
            'name': name,
            'plugin_name': plugin_name,
            'hadoop_version': hadoop_version,
        }

        self._copy_if_defined(data,
                              description=description,
                              cluster_configs=cluster_configs,
                              node_groups=node_groups,
                              anti_affinity=anti_affinity,
                              neutron_management_network=net_id,
                              default_image_id=default_image_id,
                              use_autoconfig=use_autoconfig,
                              shares=shares,
                              is_public=is_public,
                              is_protected=is_protected)

        return self._create('/cluster-templates', data, 'cluster_template')

    def update(self, cluster_template_id, name=None, plugin_name=None,
               hadoop_version=None, description=None, cluster_configs=None,
               node_groups=None, anti_affinity=None, net_id=None,
               default_image_id=None, use_autoconfig=None, shares=None,
               is_public=None, is_protected=None):

        data = {}
        self._copy_if_defined(data, name=name,
                              plugin_name=plugin_name,
                              hadoop_version=hadoop_version,
                              description=description,
                              cluster_configs=cluster_configs,
                              node_groups=node_groups,
                              anti_affinity=anti_affinity,
                              neutron_management_network=net_id,
                              default_image_id=default_image_id,
                              use_autoconfig=use_autoconfig,
                              shares=shares,
                              is_public=is_public,
                              is_protected=is_protected)

        return self._update('/cluster-templates/%s' % cluster_template_id,
                            data, 'cluster_template')

    def list(self, search_opts=None):
        query = base.get_query_string(search_opts)
        return self._list('/cluster-templates%s' % query, 'cluster_templates')

    def get(self, cluster_template_id):
        return self._get('/cluster-templates/%s' % cluster_template_id,
                         'cluster_template')

    def delete(self, cluster_template_id):
        self._delete('/cluster-templates/%s' % cluster_template_id)
