# Copyright (c) 2018 Red Hat Inc.
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

from osc_lib import utils as osc_utils

from saharaclient.osc import utils
from saharaclient.osc.v1 import node_group_templates as ngt_v1

NGT_FIELDS = ['id', 'name', 'plugin_name', 'plugin_version', 'node_processes',
              'description', 'auto_security_group', 'security_groups',
              'availability_zone', 'flavor_id', 'floating_ip_pool',
              'volumes_per_node', 'volumes_size',
              'volume_type', 'volume_local_to_instance', 'volume_mount_prefix',
              'volumes_availability_zone', 'use_autoconfig',
              'is_proxy_gateway', 'is_default', 'is_protected', 'is_public',
              'boot_from_volume', 'boot_volume_type',
              'boot_volume_availability_zone', 'boot_volume_local_to_instance']


def _format_ngt_output(data):
    data['node_processes'] = osc_utils.format_list(data['node_processes'])
    if data['volumes_per_node'] == 0:
        del data['volume_local_to_instance']
        del data['volume_mount_prefix']
        del data['volume_type'],
        del data['volumes_availability_zone']
        del data['volumes_size']
    if not data['boot_from_volume']:
        del data['boot_volume_type']
        del data['boot_volume_availability_zone']
        del data['boot_volume_local_to_instance']


class CreateNodeGroupTemplate(ngt_v1.CreateNodeGroupTemplate,
                              utils.NodeGroupTemplatesUtils):
    """Creates node group template"""

    def get_parser(self, prog_name):
        parser = super(CreateNodeGroupTemplate, self).get_parser(prog_name)

        parser.add_argument(
            '--boot-from-volume',
            action='store_true',
            default=False,
            help="Make the node group bootable from volume",
        )
        parser.add_argument(
            '--boot-volume-type',
            metavar="<boot-volume-type>",
            help='Type of the boot volume. '
                 'This parameter will be taken into account only '
                 'if booting from volume.'
        )
        parser.add_argument(
            '--boot-volume-availability-zone',
            metavar="<boot-volume-availability-zone>",
            help='Name of the availability zone to create boot volume in.'
                 ' This parameter will be taken into account only '
                 'if booting from volume.'
        )
        parser.add_argument(
            '--boot-volume-local-to-instance',
            action='store_true',
            default=False,
            help='Instance and volume guaranteed on the same host. '
                 'This parameter will be taken into account only '
                 'if booting from volume.'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._create_take_action(client, self.app, parsed_args)

        _format_ngt_output(data)
        data = utils.prepare_data(data, NGT_FIELDS)

        return self.dict2columns(data)


class ListNodeGroupTemplates(ngt_v1.ListNodeGroupTemplates,
                             utils.NodeGroupTemplatesUtils):
    """Lists node group templates"""

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        return self._list_take_action(client, self.app, parsed_args)


class ShowNodeGroupTemplate(ngt_v1.ShowNodeGroupTemplate,
                            utils.NodeGroupTemplatesUtils):
    """Display node group template details"""

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = utils.get_resource(
            client.node_group_templates,
            parsed_args.node_group_template).to_dict()

        _format_ngt_output(data)

        data = utils.prepare_data(data, NGT_FIELDS)

        return self.dict2columns(data)


class DeleteNodeGroupTemplate(ngt_v1.DeleteNodeGroupTemplate,
                              utils.NodeGroupTemplatesUtils):
    """Deletes node group template"""

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        for ngt in parsed_args.node_group_template:
            ngt_id = utils.get_resource_id(
                client.node_group_templates, ngt)
            client.node_group_templates.delete(ngt_id)
            sys.stdout.write(
                'Node group template "{ngt}" has been removed '
                'successfully.\n'.format(ngt=ngt))


class UpdateNodeGroupTemplate(ngt_v1.UpdateNodeGroupTemplate,
                              utils.NodeGroupTemplatesUtils):
    """Updates node group template"""

    def get_parser(self, prog_name):
        parser = super(UpdateNodeGroupTemplate, self).get_parser(prog_name)

        bootfromvolume = parser.add_mutually_exclusive_group()
        bootfromvolume.add_argument(
            '--boot-from-volume-enable',
            action='store_true',
            help='Makes node group bootable from volume.',
            dest='boot_from_volume'
        )
        bootfromvolume.add_argument(
            '--boot-from-volume-disable',
            action='store_false',
            help='Makes node group not bootable from volume.',
            dest='boot_from_volume'
        )
        parser.add_argument(
            '--boot-volume-type',
            metavar="<boot-volume-type>",
            help='Type of the boot volume. '
                 'This parameter will be taken into account only '
                 'if booting from volume.'
        )
        parser.add_argument(
            '--boot-volume-availability-zone',
            metavar="<boot-volume-availability-zone>",
            help='Name of the availability zone to create boot volume in.'
                 ' This parameter will be taken into account only '
                 'if booting from volume.'
        )
        bfv_locality = parser.add_mutually_exclusive_group()
        bfv_locality.add_argument(
            '--boot-volume-local-to-instance-enable',
            action='store_true',
            help='Makes boot volume explicitly local to instance.',
            dest='boot_volume_local_to_instance'
        )
        bfv_locality.add_argument(
            '--boot-volume-local-to-instance-disable',
            action='store_false',
            help='Removes explicit instruction of boot volume locality.',
            dest='boot_volume_local_to_instance'
        )
        parser.set_defaults(is_public=None, is_protected=None,
                            is_proxy_gateway=None, volume_locality=None,
                            use_auto_security_group=None, use_autoconfig=None,
                            boot_from_volume=None, boot_volume_type=None,
                            boot_volume_availability_zone=None,
                            boot_volume_local_to_instance=None)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._update_take_action(client, self.app, parsed_args)

        _format_ngt_output(data)
        data = utils.prepare_data(data, NGT_FIELDS)

        return self.dict2columns(data)


class ImportNodeGroupTemplate(ngt_v1.ImportNodeGroupTemplate,
                              utils.NodeGroupTemplatesUtils):
    """Imports node group template"""

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._import_take_action(client, parsed_args)

        _format_ngt_output(data)
        data = utils.prepare_data(data, NGT_FIELDS)

        return self.dict2columns(data)


class ExportNodeGroupTemplate(ngt_v1.ExportNodeGroupTemplate,
                              utils.NodeGroupTemplatesUtils):
    """Export node group template to JSON"""

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        self._export_take_action(client, parsed_args)
