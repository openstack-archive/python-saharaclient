# Copyright (c) 2015 Mirantis Inc.
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

import sys
import time

from osc_lib import exceptions
from osc_lib import utils as osc_utils
from oslo_serialization import jsonutils as json
from oslo_utils import timeutils
from oslo_utils import uuidutils

from saharaclient.api import base


def get_resource(manager, name_or_id, **kwargs):
    if uuidutils.is_uuid_like(name_or_id):
        return manager.get(name_or_id, **kwargs)
    else:
        resource = manager.find_unique(name=name_or_id)
        if kwargs:
            # we really need additional call to apply kwargs
            resource = manager.get(resource.id, **kwargs)
        return resource


def created_at_sorted(objs, reverse=False):
    return sorted(objs, key=created_at_key, reverse=reverse)


def random_name(prefix=None):
    return "%s-%s" % (prefix, uuidutils.generate_uuid()[:8])


def created_at_key(obj):
    return timeutils.parse_isotime(obj["created_at"])


def get_resource_id(manager, name_or_id):
    if uuidutils.is_uuid_like(name_or_id):
        return name_or_id
    else:
        return manager.find_unique(name=name_or_id).id


def create_dict_from_kwargs(**kwargs):
    return {k: v for (k, v) in kwargs.items() if v is not None}


def prepare_data(data, fields):
    new_data = {}
    for f in fields:
        if f in data:
            new_data[f.replace('_', ' ').capitalize()] = data[f]

    return new_data


def unzip(data):
    return zip(*data)


def extend_columns(columns, items):
    return unzip(list(unzip(columns)) + [('', '')] + items)


def prepare_column_headers(columns, remap=None):
    remap = remap if remap else {}
    new_columns = []
    for c in columns:
        for old, new in remap.items():
            c = c.replace(old, new)
        new_columns.append(c.replace('_', ' ').capitalize())

    return new_columns


def get_by_name_substring(data, name):
    return [obj for obj in data if name in obj.name]


def wait_for_delete(manager, obj_id, sleep_time=5, timeout=3000):
    s_time = timeutils.utcnow()
    while timeutils.delta_seconds(s_time, timeutils.utcnow()) < timeout:
        try:
            manager.get(obj_id)
        except base.APIException as ex:
            if ex.error_code == 404:
                return True
            raise
        time.sleep(sleep_time)

    return False


def create_node_group_templates(client, app,  parsed_args, flavor_id, configs,
                                shares):
    if app.api_version['data_processing'] == '2':
        data = client.node_group_templates.create(
            name=parsed_args.name,
            plugin_name=parsed_args.plugin,
            plugin_version=parsed_args.plugin_version,
            flavor_id=flavor_id,
            description=parsed_args.description,
            volumes_per_node=parsed_args.volumes_per_node,
            volumes_size=parsed_args.volumes_size,
            node_processes=parsed_args.processes,
            floating_ip_pool=parsed_args.floating_ip_pool,
            security_groups=parsed_args.security_groups,
            auto_security_group=parsed_args.auto_security_group,
            availability_zone=parsed_args.availability_zone,
            volume_type=parsed_args.volumes_type,
            is_proxy_gateway=parsed_args.proxy_gateway,
            volume_local_to_instance=parsed_args.volumes_locality,
            use_autoconfig=parsed_args.autoconfig,
            is_public=parsed_args.public,
            is_protected=parsed_args.protected,
            node_configs=configs,
            shares=shares,
            volumes_availability_zone=(
                parsed_args.volumes_availability_zone),
            volume_mount_prefix=parsed_args.volumes_mount_prefix,
            boot_from_volume=parsed_args.boot_from_volume).to_dict()
    else:
        data = client.node_group_templates.create(
            name=parsed_args.name,
            plugin_name=parsed_args.plugin,
            hadoop_version=parsed_args.plugin_version,
            flavor_id=flavor_id,
            description=parsed_args.description,
            volumes_per_node=parsed_args.volumes_per_node,
            volumes_size=parsed_args.volumes_size,
            node_processes=parsed_args.processes,
            floating_ip_pool=parsed_args.floating_ip_pool,
            security_groups=parsed_args.security_groups,
            auto_security_group=parsed_args.auto_security_group,
            availability_zone=parsed_args.availability_zone,
            volume_type=parsed_args.volumes_type,
            is_proxy_gateway=parsed_args.proxy_gateway,
            volume_local_to_instance=parsed_args.volumes_locality,
            use_autoconfig=parsed_args.autoconfig,
            is_public=parsed_args.public,
            is_protected=parsed_args.protected,
            node_configs=configs,
            shares=shares,
            volumes_availability_zone=(
                parsed_args.volumes_availability_zone),
            volume_mount_prefix=parsed_args.volumes_mount_prefix).to_dict()
    return data


class NodeGroupTemplatesUtils(object):

    def _create_take_action(self, client, app, parsed_args):
        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = json.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))
            data = client.node_group_templates.create(**template).to_dict()
        else:
            if (not parsed_args.name or not parsed_args.plugin or
                    not parsed_args.plugin_version or not parsed_args.flavor or
                    not parsed_args.processes):
                raise exceptions.CommandError(
                    'At least --name, --plugin, --plugin-version, --processes,'
                    ' --flavor arguments should be specified or json template '
                    'should be provided with --json argument')

            configs = None
            if parsed_args.configs:
                blob = osc_utils.read_blob_file_contents(parsed_args.configs)
                try:
                    configs = json.loads(blob)
                except ValueError as e:
                    raise exceptions.CommandError(
                        'An error occurred when reading '
                        'configs from file %s: %s' % (parsed_args.configs, e))

            shares = None
            if parsed_args.shares:
                blob = osc_utils.read_blob_file_contents(parsed_args.shares)
                try:
                    shares = json.loads(blob)
                except ValueError as e:
                    raise exceptions.CommandError(
                        'An error occurred when reading '
                        'shares from file %s: %s' % (parsed_args.shares, e))

            compute_client = app.client_manager.compute
            flavor_id = osc_utils.find_resource(
                compute_client.flavors, parsed_args.flavor).id

            data = create_node_group_templates(client, app, parsed_args,
                                               flavor_id, configs, shares)

        return data

    def _list_take_action(self, client, app, parsed_args):
        search_opts = {}
        if parsed_args.plugin:
            search_opts['plugin_name'] = parsed_args.plugin
        if parsed_args.plugin_version:
            search_opts['hadoop_version'] = parsed_args.plugin_version

        data = client.node_group_templates.list(search_opts=search_opts)

        if parsed_args.name:
            data = get_by_name_substring(data, parsed_args.name)

        if app.api_version['data_processing'] == '2':
            if parsed_args.long:
                columns = ('name', 'id', 'plugin_name', 'plugin_version',
                           'node_processes', 'description')
                column_headers = prepare_column_headers(columns)

            else:
                columns = ('name', 'id', 'plugin_name', 'plugin_version')
                column_headers = prepare_column_headers(columns)
        else:
            if parsed_args.long:
                columns = ('name', 'id', 'plugin_name', 'hadoop_version',
                           'node_processes', 'description')
                column_headers = prepare_column_headers(
                    columns, {'hadoop_version': 'plugin_version'})

            else:
                columns = ('name', 'id', 'plugin_name', 'hadoop_version')
                column_headers = prepare_column_headers(
                    columns, {'hadoop_version': 'plugin_version'})

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns,
                formatters={
                    'node_processes': osc_utils.format_list
                }
            ) for s in data)
        )

    def _update_take_action(self, client, app, parsed_args):
        ngt_id = get_resource_id(
            client.node_group_templates, parsed_args.node_group_template)

        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = json.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))
            data = client.node_group_templates.update(
                ngt_id, **template).to_dict()
        else:
            configs = None
            if parsed_args.configs:
                blob = osc_utils.read_blob_file_contents(parsed_args.configs)
                try:
                    configs = json.loads(blob)
                except ValueError as e:
                    raise exceptions.CommandError(
                        'An error occurred when reading '
                        'configs from file %s: %s' % (parsed_args.configs, e))

            shares = None
            if parsed_args.shares:
                blob = osc_utils.read_blob_file_contents(parsed_args.shares)
                try:
                    shares = json.loads(blob)
                except ValueError as e:
                    raise exceptions.CommandError(
                        'An error occurred when reading '
                        'shares from file %s: %s' % (parsed_args.shares, e))

            flavor_id = None
            if parsed_args.flavor:
                compute_client = self.app.client_manager.compute
                flavor_id = osc_utils.find_resource(
                    compute_client.flavors, parsed_args.flavor).id

            update_dict = create_dict_from_kwargs(
                name=parsed_args.name,
                plugin_name=parsed_args.plugin,
                hadoop_version=parsed_args.plugin_version,
                flavor_id=flavor_id,
                description=parsed_args.description,
                volumes_per_node=parsed_args.volumes_per_node,
                volumes_size=parsed_args.volumes_size,
                node_processes=parsed_args.processes,
                floating_ip_pool=parsed_args.floating_ip_pool,
                security_groups=parsed_args.security_groups,
                auto_security_group=parsed_args.use_auto_security_group,
                availability_zone=parsed_args.availability_zone,
                volume_type=parsed_args.volumes_type,
                is_proxy_gateway=parsed_args.is_proxy_gateway,
                volume_local_to_instance=parsed_args.volume_locality,
                use_autoconfig=parsed_args.use_autoconfig,
                is_public=parsed_args.is_public,
                is_protected=parsed_args.is_protected,
                node_configs=configs,
                shares=shares,
                volumes_availability_zone=(
                    parsed_args.volumes_availability_zone),
                volume_mount_prefix=parsed_args.volumes_mount_prefix
            )

            if app.api_version['data_processing'] == '2':
                if 'hadoop_version' in update_dict:
                    update_dict.pop('hadoop_version')
                    update_dict['plugin_version'] = parsed_args.plugin_version
                if parsed_args.boot_from_volume is not None:
                    update_dict['boot_from_volume'] = (
                        parsed_args.boot_from_volume)
            data = client.node_group_templates.update(
                ngt_id, **update_dict).to_dict()

        return data

    def _import_take_action(self, client, parsed_args):
        if (not parsed_args.image_id or
                not parsed_args.flavor_id):
            raise exceptions.CommandError(
                'At least --image_id and --flavor_id should be specified')
        blob = osc_utils.read_blob_file_contents(parsed_args.json)
        try:
            template = json.loads(blob)
        except ValueError as e:
            raise exceptions.CommandError(
                'An error occurred when reading '
                'template from file %s: %s' % (parsed_args.json, e))
        template['node_group_template']['floating_ip_pool'] = (
            parsed_args.floating_ip_pool)
        template['node_group_template']['image_id'] = (
            parsed_args.image_id)
        template['node_group_template']['flavor_id'] = (
            parsed_args.flavor_id)
        template['node_group_template']['security_groups'] = (
            parsed_args.security_groups)
        if parsed_args.name:
            template['node_group_template']['name'] = parsed_args.name
        data = client.node_group_templates.create(
            **template['node_group_template']).to_dict()

        return data

    def _export_take_action(self, client, parsed_args):
        ngt_id = get_resource_id(
            client.node_group_templates, parsed_args.node_group_template)
        response = client.node_group_templates.export(ngt_id)
        result = json.dumps(response._info, indent=4)+"\n"
        if parsed_args.file:
            with open(parsed_args.file, "w+") as file:
                file.write(result)
        else:
            sys.stdout.write(result)
