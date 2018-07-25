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

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from saharaclient.osc import utils

NGT_FIELDS = ['id', 'name', 'plugin_name', 'plugin_version', 'node_processes',
              'description', 'auto_security_group', 'security_groups',
              'availability_zone', 'flavor_id', 'floating_ip_pool',
              'volumes_per_node', 'volumes_size',
              'volume_type', 'volume_local_to_instance', 'volume_mount_prefix',
              'volumes_availability_zone', 'use_autoconfig',
              'is_proxy_gateway', 'is_default', 'is_protected', 'is_public']


def _format_ngt_output(data):
    data['node_processes'] = osc_utils.format_list(data['node_processes'])
    data['plugin_version'] = data.pop('hadoop_version')
    if data['volumes_per_node'] == 0:
        del data['volume_local_to_instance']
        del data['volume_mount_prefix']
        del data['volume_type'],
        del data['volumes_availability_zone']
        del data['volumes_size']


class CreateNodeGroupTemplate(command.ShowOne, utils.NodeGroupTemplatesUtils):
    """Creates node group template"""

    log = logging.getLogger(__name__ + ".CreateNodeGroupTemplate")

    def get_parser(self, prog_name):
        parser = super(CreateNodeGroupTemplate, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar="<name>",
            help="Name of the node group template [REQUIRED if JSON is not "
                 "provided]",
        )
        parser.add_argument(
            '--plugin',
            metavar="<plugin>",
            help="Name of the plugin [REQUIRED if JSON is not provided]"
        )
        parser.add_argument(
            '--plugin-version',
            metavar="<plugin_version>",
            help="Version of the plugin [REQUIRED if JSON is not provided]"
        )
        parser.add_argument(
            '--processes',
            metavar="<processes>",
            nargs="+",
            help="List of the processes that will be launched on each "
                 "instance [REQUIRED if JSON is not provided]"
        )
        parser.add_argument(
            '--flavor',
            metavar="<flavor>",
            help="Name or ID of the flavor [REQUIRED if JSON is not provided]"
        )
        parser.add_argument(
            '--security-groups',
            metavar="<security-groups>",
            nargs="+",
            help="List of the security groups for the instances in this node "
                 "group"
        )
        parser.add_argument(
            '--auto-security-group',
            action='store_true',
            default=False,
            help='Indicates if an additional security group should be created '
                 'for the node group',
        )
        parser.add_argument(
            '--availability-zone',
            metavar="<availability-zone>",
            help="Name of the availability zone where instances "
                 "will be created"
        )
        parser.add_argument(
            '--floating-ip-pool',
            metavar="<floating-ip-pool>",
            help="ID of the floating IP pool"
        )
        parser.add_argument(
            '--volumes-per-node',
            type=int,
            metavar="<volumes-per-node>",
            help="Number of volumes attached to every node"
        )
        parser.add_argument(
            '--volumes-size',
            type=int,
            metavar="<volumes-size>",
            help='Size of volumes attached to node (GB). '
                 'This parameter will be taken into account only '
                 'if volumes-per-node is set and non-zero'
        )
        parser.add_argument(
            '--volumes-type',
            metavar="<volumes-type>",
            help='Type of the volumes. '
                 'This parameter will be taken into account only '
                 'if volumes-per-node is set and non-zero'
        )
        parser.add_argument(
            '--volumes-availability-zone',
            metavar="<volumes-availability-zone>",
            help='Name of the availability zone where volumes will be created.'
                 ' This parameter will be taken into account only '
                 'if volumes-per-node is set and non-zero'
        )
        parser.add_argument(
            '--volumes-mount-prefix',
            metavar="<volumes-mount-prefix>",
            help='Prefix for mount point directory. '
                 'This parameter will be taken into account only '
                 'if volumes-per-node is set and non-zero'
        )
        parser.add_argument(
            '--volumes-locality',
            action='store_true',
            default=False,
            help='If enabled, instance and attached volumes will be created on'
                 ' the same physical host. This parameter will be taken into '
                 'account only if volumes-per-node is set and non-zero',
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help='Description of the node group template'
        )
        parser.add_argument(
            '--autoconfig',
            action='store_true',
            default=False,
            help='If enabled, instances of the node group will be '
                 'automatically configured',
        )
        parser.add_argument(
            '--proxy-gateway',
            action='store_true',
            default=False,
            help='If enabled, instances of the node group will be used to '
                 'access other instances in the cluster',
        )
        parser.add_argument(
            '--public',
            action='store_true',
            default=False,
            help='Make the node group template public (Visible from other '
                 'projects)',
        )
        parser.add_argument(
            '--protected',
            action='store_true',
            default=False,
            help='Make the node group template protected',
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the node group template. Other '
                 'arguments will not be taken into account if this one is '
                 'provided'
        )
        parser.add_argument(
            '--shares',
            metavar='<filename>',
            help='JSON representation of the manila shares'
        )
        parser.add_argument(
            '--configs',
            metavar='<filename>',
            help='JSON representation of the node group template configs'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._create_take_action(client, self.app, parsed_args)

        _format_ngt_output(data)
        data = utils.prepare_data(data, NGT_FIELDS)

        return self.dict2columns(data)


class ListNodeGroupTemplates(command.Lister, utils.NodeGroupTemplatesUtils):
    """Lists node group templates"""

    log = logging.getLogger(__name__ + ".ListNodeGroupTemplates")

    def get_parser(self, prog_name):
        parser = super(ListNodeGroupTemplates, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--plugin',
            metavar="<plugin>",
            help="List node group templates for specific plugin"
        )

        parser.add_argument(
            '--plugin-version',
            metavar="<plugin_version>",
            help="List node group templates with specific version of the "
                 "plugin"
        )

        parser.add_argument(
            '--name',
            metavar="<name-substring>",
            help="List node group templates with specific substring in the "
                 "name"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        return self._list_take_action(client, self.app, parsed_args)


class ShowNodeGroupTemplate(command.ShowOne, utils.NodeGroupTemplatesUtils):
    """Display node group template details"""

    log = logging.getLogger(__name__ + ".ShowNodeGroupTemplate")

    def get_parser(self, prog_name):
        parser = super(ShowNodeGroupTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "node_group_template",
            metavar="<node-group-template>",
            help="Name or id of the node group template to display",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = utils.get_resource(
            client.node_group_templates,
            parsed_args.node_group_template).to_dict()

        _format_ngt_output(data)

        data = utils.prepare_data(data, NGT_FIELDS)

        return self.dict2columns(data)


class DeleteNodeGroupTemplate(command.Command, utils.NodeGroupTemplatesUtils):
    """Deletes node group template"""

    log = logging.getLogger(__name__ + ".DeleteNodeGroupTemplate")

    def get_parser(self, prog_name):
        parser = super(DeleteNodeGroupTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "node_group_template",
            metavar="<node-group-template>",
            nargs="+",
            help="Name(s) or id(s) of the node group template(s) to delete",
        )

        return parser

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


class UpdateNodeGroupTemplate(command.ShowOne, utils.NodeGroupTemplatesUtils):
    """Updates node group template"""

    log = logging.getLogger(__name__ + ".UpdateNodeGroupTemplate")

    def get_parser(self, prog_name):
        parser = super(UpdateNodeGroupTemplate, self).get_parser(prog_name)

        parser.add_argument(
            'node_group_template',
            metavar="<node-group-template>",
            help="Name or ID of the node group template",
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help="New name of the node group template",
        )
        parser.add_argument(
            '--plugin',
            metavar="<plugin>",
            help="Name of the plugin"
        )
        parser.add_argument(
            '--plugin-version',
            metavar="<plugin_version>",
            help="Version of the plugin"
        )
        parser.add_argument(
            '--processes',
            metavar="<processes>",
            nargs="+",
            help="List of the processes that will be launched on each "
                 "instance"
        )
        parser.add_argument(
            '--security-groups',
            metavar="<security-groups>",
            nargs="+",
            help="List of the security groups for the instances in this node "
                 "group"
        )
        autosecurity = parser.add_mutually_exclusive_group()
        autosecurity.add_argument(
            '--auto-security-group-enable',
            action='store_true',
            help='Additional security group should be created '
                 'for the node group',
            dest='use_auto_security_group'
        )
        autosecurity.add_argument(
            '--auto-security-group-disable',
            action='store_false',
            help='Additional security group should not be created '
                 'for the node group',
            dest='use_auto_security_group'
        )
        parser.add_argument(
            '--availability-zone',
            metavar="<availability-zone>",
            help="Name of the availability zone where instances "
                 "will be created"
        )
        parser.add_argument(
            '--flavor',
            metavar="<flavor>",
            help="Name or ID of the flavor"
        )
        parser.add_argument(
            '--floating-ip-pool',
            metavar="<floating-ip-pool>",
            help="ID of the floating IP pool"
        )
        parser.add_argument(
            '--volumes-per-node',
            type=int,
            metavar="<volumes-per-node>",
            help="Number of volumes attached to every node"
        )
        parser.add_argument(
            '--volumes-size',
            type=int,
            metavar="<volumes-size>",
            help='Size of volumes attached to node (GB). '
                 'This parameter will be taken into account only '
                 'if volumes-per-node is set and non-zero'
        )
        parser.add_argument(
            '--volumes-type',
            metavar="<volumes-type>",
            help='Type of the volumes. '
                 'This parameter will be taken into account only '
                 'if volumes-per-node is set and non-zero'
        )
        parser.add_argument(
            '--volumes-availability-zone',
            metavar="<volumes-availability-zone>",
            help='Name of the availability zone where volumes will be created.'
                 ' This parameter will be taken into account only '
                 'if volumes-per-node is set and non-zero'
        )
        parser.add_argument(
            '--volumes-mount-prefix',
            metavar="<volumes-mount-prefix>",
            help='Prefix for mount point directory. '
                 'This parameter will be taken into account only '
                 'if volumes-per-node is set and non-zero'
        )
        volumelocality = parser.add_mutually_exclusive_group()
        volumelocality.add_argument(
            '--volumes-locality-enable',
            action='store_true',
            help='Instance and attached volumes will be created on '
                 'the same physical host. This parameter will be taken into '
                 'account only if volumes-per-node is set and non-zero',
            dest='volume_locality'
        )
        volumelocality.add_argument(
            '--volumes-locality-disable',
            action='store_false',
            help='Instance and attached volumes creation on the same physical '
                 'host will not be regulated. This parameter will be taken'
                 'into account only if volumes-per-node is set and non-zero',
            dest='volume_locality'
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help='Description of the node group template'
        )
        autoconfig = parser.add_mutually_exclusive_group()
        autoconfig.add_argument(
            '--autoconfig-enable',
            action='store_true',
            help='Instances of the node group will be '
                 'automatically configured',
            dest='use_autoconfig'
        )
        autoconfig.add_argument(
            '--autoconfig-disable',
            action='store_false',
            help='Instances of the node group will not be '
                 'automatically configured',
            dest='use_autoconfig'
        )
        proxy = parser.add_mutually_exclusive_group()
        proxy.add_argument(
            '--proxy-gateway-enable',
            action='store_true',
            help='Instances of the node group will be used to '
                 'access other instances in the cluster',
            dest='is_proxy_gateway'
        )
        proxy.add_argument(
            '--proxy-gateway-disable',
            action='store_false',
            help='Instances of the node group will not be used to '
                 'access other instances in the cluster',
            dest='is_proxy_gateway'
        )
        public = parser.add_mutually_exclusive_group()
        public.add_argument(
            '--public',
            action='store_true',
            help='Make the node group template public '
                 '(Visible from other projects)',
            dest='is_public'
        )
        public.add_argument(
            '--private',
            action='store_false',
            help='Make the node group template private '
                 '(Visible only from this project)',
            dest='is_public'
        )
        protected = parser.add_mutually_exclusive_group()
        protected.add_argument(
            '--protected',
            action='store_true',
            help='Make the node group template protected',
            dest='is_protected'
        )
        protected.add_argument(
            '--unprotected',
            action='store_false',
            help='Make the node group template unprotected',
            dest='is_protected'
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the node group template update '
                 'fields. Other arguments will not be taken into account if '
                 'this one is provided'
        )
        parser.add_argument(
            '--shares',
            metavar='<filename>',
            help='JSON representation of the manila shares'
        )
        parser.add_argument(
            '--configs',
            metavar='<filename>',
            help='JSON representation of the node group template configs'
        )
        parser.set_defaults(is_public=None, is_protected=None,
                            is_proxy_gateway=None, volume_locality=None,
                            use_auto_security_group=None, use_autoconfig=None)
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._update_take_action(client, self.app, parsed_args)

        _format_ngt_output(data)
        data = utils.prepare_data(data, NGT_FIELDS)

        return self.dict2columns(data)


class ImportNodeGroupTemplate(command.ShowOne, utils.NodeGroupTemplatesUtils):
    """Imports node group template"""

    log = logging.getLogger(__name__ + ".ImportNodeGroupTemplate")

    def get_parser(self, prog_name):
        parser = super(ImportNodeGroupTemplate, self).get_parser(prog_name)

        parser.add_argument(
            'json',
            metavar="<json>",
            help="JSON containing node group template",
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help="Name of the node group template",
        )
        parser.add_argument(
            '--security_groups',
            metavar="<security_groups>",
            help="Security groups of the node group template"
        )
        parser.add_argument(
            '--floating_ip_pool',
            metavar="<floating_ip_pool>",
            help="Floating IP pool of the node group template"
        )
        parser.add_argument(
            '--image_id',
            metavar="<image_id>",
            required=True,
            help="Image ID of the node group template",
        )
        parser.add_argument(
            '--flavor_id',
            metavar="<flavor_id>",
            required=True,
            help="Flavor ID of the node group template",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._import_take_action(client, parsed_args)

        _format_ngt_output(data)
        data = utils.prepare_data(data, NGT_FIELDS)

        return self.dict2columns(data)


class ExportNodeGroupTemplate(command.Command, utils.NodeGroupTemplatesUtils):
    """Export node group template to JSON"""

    log = logging.getLogger(__name__ + ".ExportNodeGroupTemplate")

    def get_parser(self, prog_name):
        parser = super(ExportNodeGroupTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "node_group_template",
            metavar="<node-group-template>",
            help="Name or id of the node group template to export",
        )
        parser.add_argument(
            "--file",
            metavar="<filename>",
            help="Name of the file node group template should be exported to."
                 "If not provided, print to stdout",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        self._export_take_action(client, parsed_args)
