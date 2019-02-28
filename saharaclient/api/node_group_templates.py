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


class NodeGroupTemplate(base.Resource):
    resource_name = 'Node Group Template'


class NodeGroupTemplateManagerV1(base.ResourceManager):
    resource_class = NodeGroupTemplate
    NotUpdated = base.NotUpdated()

    def create(self, name, plugin_name, hadoop_version, flavor_id,
               description=None, volumes_per_node=None, volumes_size=None,
               node_processes=None, node_configs=None, floating_ip_pool=None,
               security_groups=None, auto_security_group=None,
               availability_zone=None, volumes_availability_zone=None,
               volume_type=None, image_id=None, is_proxy_gateway=None,
               volume_local_to_instance=None, use_autoconfig=None,
               shares=None, is_public=None, is_protected=None,
               volume_mount_prefix=None):
        """Create a Node Group Template."""

        data = {
            'name': name,
            'plugin_name': plugin_name,
            'hadoop_version': hadoop_version,
            'flavor_id': flavor_id,
            'node_processes': node_processes
        }

        return self._do_create(data, description, volumes_per_node,
                               volumes_size, node_configs, floating_ip_pool,
                               security_groups, auto_security_group,
                               availability_zone, volumes_availability_zone,
                               volume_type, image_id, is_proxy_gateway,
                               volume_local_to_instance, use_autoconfig,
                               shares, is_public, is_protected,
                               volume_mount_prefix)

    def _do_create(self, data, description, volumes_per_node, volumes_size,
                   node_configs, floating_ip_pool, security_groups,
                   auto_security_group, availability_zone,
                   volumes_availability_zone, volume_type, image_id,
                   is_proxy_gateway, volume_local_to_instance, use_autoconfig,
                   shares, is_public, is_protected, volume_mount_prefix,
                   boot_from_volume=None, boot_volume_type=None,
                   boot_volume_az=None, boot_volume_local=None):

        self._copy_if_defined(data,
                              description=description,
                              node_configs=node_configs,
                              floating_ip_pool=floating_ip_pool,
                              security_groups=security_groups,
                              auto_security_group=auto_security_group,
                              availability_zone=availability_zone,
                              image_id=image_id,
                              is_proxy_gateway=is_proxy_gateway,
                              use_autoconfig=use_autoconfig,
                              shares=shares,
                              is_public=is_public,
                              is_protected=is_protected,
                              boot_from_volume=boot_from_volume,
                              boot_volume_type=boot_volume_type,
                              boot_volume_availability_zone=boot_volume_az,
                              boot_volume_local_to_instance=boot_volume_local
                              )

        if volumes_per_node:
            data.update({"volumes_per_node": volumes_per_node,
                         "volumes_size": volumes_size})
            if volumes_availability_zone:
                data.update({"volumes_availability_zone":
                             volumes_availability_zone})
            if volume_type:
                data.update({"volume_type": volume_type})
            if volume_local_to_instance:
                data.update(
                    {"volume_local_to_instance": volume_local_to_instance})
            if volume_mount_prefix:
                data.update({"volume_mount_prefix": volume_mount_prefix})

        return self._create('/node-group-templates', data,
                            'node_group_template')

    def update(self, ng_template_id, name=NotUpdated, plugin_name=NotUpdated,
               hadoop_version=NotUpdated, flavor_id=NotUpdated,
               description=NotUpdated, volumes_per_node=NotUpdated,
               volumes_size=NotUpdated, node_processes=NotUpdated,
               node_configs=NotUpdated, floating_ip_pool=NotUpdated,
               security_groups=NotUpdated, auto_security_group=NotUpdated,
               availability_zone=NotUpdated,
               volumes_availability_zone=NotUpdated, volume_type=NotUpdated,
               image_id=NotUpdated, is_proxy_gateway=NotUpdated,
               volume_local_to_instance=NotUpdated, use_autoconfig=NotUpdated,
               shares=NotUpdated, is_public=NotUpdated,
               is_protected=NotUpdated, volume_mount_prefix=NotUpdated):
        """Update a Node Group Template."""

        data = {}
        self._copy_if_updated(
            data, name=name, plugin_name=plugin_name,
            hadoop_version=hadoop_version, flavor_id=flavor_id,
            description=description, volumes_per_node=volumes_per_node,
            volumes_size=volumes_size, node_processes=node_processes,
            node_configs=node_configs, floating_ip_pool=floating_ip_pool,
            security_groups=security_groups,
            auto_security_group=auto_security_group,
            availability_zone=availability_zone,
            volumes_availability_zone=volumes_availability_zone,
            volume_type=volume_type, image_id=image_id,
            is_proxy_gateway=is_proxy_gateway,
            volume_local_to_instance=volume_local_to_instance,
            use_autoconfig=use_autoconfig, shares=shares,
            is_public=is_public, is_protected=is_protected,
            volume_mount_prefix=volume_mount_prefix
        )

        return self._update('/node-group-templates/%s' % ng_template_id, data,
                            'node_group_template')

    def list(self, search_opts=None, marker=None,
             limit=None, sort_by=None, reverse=None):
        """Get a list of Node Group Templates."""
        query = base.get_query_string(search_opts, limit=limit, marker=marker,
                                      sort_by=sort_by, reverse=reverse)
        url = "/node-group-templates%s" % query
        return self._page(url, 'node_group_templates', limit)

    def get(self, ng_template_id):
        """Get information about a Node Group Template."""
        return self._get('/node-group-templates/%s' % ng_template_id,
                         'node_group_template')

    def delete(self, ng_template_id):
        """Delete a Node Group Template."""
        self._delete('/node-group-templates/%s' % ng_template_id)

    def export(self, ng_template_id):
        """Export a Node Group Template."""
        return self._get('/node-group-templates/%s/export' % ng_template_id)


class NodeGroupTemplateManagerV2(NodeGroupTemplateManagerV1):
    NotUpdated = base.NotUpdated()

    def create(self, name, plugin_name, plugin_version, flavor_id,
               description=None, volumes_per_node=None, volumes_size=None,
               node_processes=None, node_configs=None, floating_ip_pool=None,
               security_groups=None, auto_security_group=None,
               availability_zone=None, volumes_availability_zone=None,
               volume_type=None, image_id=None, is_proxy_gateway=None,
               volume_local_to_instance=None, use_autoconfig=None,
               shares=None, is_public=None, is_protected=None,
               volume_mount_prefix=None, boot_from_volume=None,
               boot_volume_type=None, boot_volume_availability_zone=None,
               boot_volume_local_to_instance=None):
        """Create a Node Group Template."""

        data = {
            'name': name,
            'plugin_name': plugin_name,
            'plugin_version': plugin_version,
            'flavor_id': flavor_id,
            'node_processes': node_processes
        }

        return self._do_create(data, description, volumes_per_node,
                               volumes_size, node_configs, floating_ip_pool,
                               security_groups, auto_security_group,
                               availability_zone, volumes_availability_zone,
                               volume_type, image_id, is_proxy_gateway,
                               volume_local_to_instance, use_autoconfig,
                               shares, is_public, is_protected,
                               volume_mount_prefix, boot_from_volume,
                               boot_volume_type,
                               boot_volume_availability_zone,
                               boot_volume_local_to_instance)

    def update(self, ng_template_id, name=NotUpdated, plugin_name=NotUpdated,
               plugin_version=NotUpdated, flavor_id=NotUpdated,
               description=NotUpdated, volumes_per_node=NotUpdated,
               volumes_size=NotUpdated, node_processes=NotUpdated,
               node_configs=NotUpdated, floating_ip_pool=NotUpdated,
               security_groups=NotUpdated, auto_security_group=NotUpdated,
               availability_zone=NotUpdated,
               volumes_availability_zone=NotUpdated, volume_type=NotUpdated,
               image_id=NotUpdated, is_proxy_gateway=NotUpdated,
               volume_local_to_instance=NotUpdated, use_autoconfig=NotUpdated,
               shares=NotUpdated, is_public=NotUpdated,
               is_protected=NotUpdated, volume_mount_prefix=NotUpdated,
               boot_from_volume=NotUpdated,
               boot_volume_type=NotUpdated,
               boot_volume_availability_zone=NotUpdated,
               boot_volume_local_to_instance=NotUpdated):
        """Update a Node Group Template."""

        data = {}
        self._copy_if_updated(
            data, name=name, plugin_name=plugin_name,
            plugin_version=plugin_version, flavor_id=flavor_id,
            description=description, volumes_per_node=volumes_per_node,
            volumes_size=volumes_size, node_processes=node_processes,
            node_configs=node_configs, floating_ip_pool=floating_ip_pool,
            security_groups=security_groups,
            auto_security_group=auto_security_group,
            availability_zone=availability_zone,
            volumes_availability_zone=volumes_availability_zone,
            volume_type=volume_type, image_id=image_id,
            is_proxy_gateway=is_proxy_gateway,
            volume_local_to_instance=volume_local_to_instance,
            use_autoconfig=use_autoconfig, shares=shares,
            is_public=is_public, is_protected=is_protected,
            volume_mount_prefix=volume_mount_prefix,
            boot_from_volume=boot_from_volume,
            boot_volume_type=boot_volume_type,
            boot_volume_availability_zone=boot_volume_availability_zone,
            boot_volume_local_to_instance=boot_volume_local_to_instance
        )

        return self._patch('/node-group-templates/%s' % ng_template_id, data,
                           'node_group_template')


# NOTE(jfreud): keep this around for backwards compatibility
NodeGroupTemplateManager = NodeGroupTemplateManagerV1
