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


class ClusterTemplateManagerV1(base.ResourceManager):
    resource_class = ClusterTemplate
    NotUpdated = base.NotUpdated()

    def create(self, name, plugin_name, hadoop_version, description=None,
               cluster_configs=None, node_groups=None, anti_affinity=None,
               net_id=None, default_image_id=None, use_autoconfig=None,
               shares=None, is_public=None, is_protected=None,
               domain_name=None):
        """Create a Cluster Template."""

        data = {
            'name': name,
            'plugin_name': plugin_name,
            'hadoop_version': hadoop_version,
        }

        return self._do_create(data, description, cluster_configs,
                               node_groups, anti_affinity, net_id,
                               default_image_id, use_autoconfig, shares,
                               is_public, is_protected, domain_name)

    def _do_create(self, data, description, cluster_configs, node_groups,
                   anti_affinity, net_id, default_image_id, use_autoconfig,
                   shares, is_public, is_protected, domain_name):

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
                              is_protected=is_protected,
                              domain_name=domain_name)

        return self._create('/cluster-templates', data, 'cluster_template')

    def update(self, cluster_template_id, name=NotUpdated,
               plugin_name=NotUpdated, hadoop_version=NotUpdated,
               description=NotUpdated, cluster_configs=NotUpdated,
               node_groups=NotUpdated, anti_affinity=NotUpdated,
               net_id=NotUpdated, default_image_id=NotUpdated,
               use_autoconfig=NotUpdated, shares=NotUpdated,
               is_public=NotUpdated, is_protected=NotUpdated,
               domain_name=NotUpdated):
        """Update a Cluster Template."""

        data = {}
        self._copy_if_updated(data, name=name,
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
                              is_protected=is_protected,
                              domain_name=domain_name)

        return self._update('/cluster-templates/%s' % cluster_template_id,
                            data, 'cluster_template')

    def list(self, search_opts=None, marker=None,
             limit=None, sort_by=None, reverse=None):
        """Get list of Cluster Templates."""
        query = base.get_query_string(search_opts, marker=marker, limit=limit,
                                      sort_by=sort_by, reverse=reverse)
        url = "/cluster-templates%s" % query
        return self._page(url, 'cluster_templates', limit)

    def get(self, cluster_template_id):
        """Get information about a Cluster Template."""
        return self._get('/cluster-templates/%s' % cluster_template_id,
                         'cluster_template')

    def delete(self, cluster_template_id):
        """Delete a Cluster Template."""
        self._delete('/cluster-templates/%s' % cluster_template_id)

    def export(self, cluster_template_id):
        """Export a Cluster Template."""
        return self._get('/cluster-templates/%s/export' % cluster_template_id)


class ClusterTemplateManagerV2(ClusterTemplateManagerV1):
    NotUpdated = base.NotUpdated()

    def create(self, name, plugin_name, plugin_version, description=None,
               cluster_configs=None, node_groups=None, anti_affinity=None,
               net_id=None, default_image_id=None, use_autoconfig=None,
               shares=None, is_public=None, is_protected=None,
               domain_name=None):
        """Create a Cluster Template."""

        data = {
            'name': name,
            'plugin_name': plugin_name,
            'plugin_version': plugin_version
        }

        return self._do_create(data, description, cluster_configs,
                               node_groups, anti_affinity, net_id,
                               default_image_id, use_autoconfig, shares,
                               is_public, is_protected, domain_name)

    def update(self, cluster_template_id, name=NotUpdated,
               plugin_name=NotUpdated, plugin_version=NotUpdated,
               description=NotUpdated, cluster_configs=NotUpdated,
               node_groups=NotUpdated, anti_affinity=NotUpdated,
               net_id=NotUpdated, default_image_id=NotUpdated,
               use_autoconfig=NotUpdated, shares=NotUpdated,
               is_public=NotUpdated, is_protected=NotUpdated,
               domain_name=NotUpdated):
        """Update a Cluster Template."""

        data = {}
        self._copy_if_updated(data, name=name,
                              plugin_name=plugin_name,
                              plugin_version=plugin_version,
                              description=description,
                              cluster_configs=cluster_configs,
                              node_groups=node_groups,
                              anti_affinity=anti_affinity,
                              neutron_management_network=net_id,
                              default_image_id=default_image_id,
                              use_autoconfig=use_autoconfig,
                              shares=shares,
                              is_public=is_public,
                              is_protected=is_protected,
                              domain_name=domain_name)

        return self._patch('/cluster-templates/%s' % cluster_template_id,
                           data, 'cluster_template')


# NOTE(jfreud): keep this around for backwards compatibility
ClusterTemplateManager = ClusterTemplateManagerV1
