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
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from oslo_log import log as logging
from oslo_serialization import jsonutils as json

from saharaclient.osc import utils

CT_FIELDS = ['id', 'name', 'plugin_name', 'plugin_version', 'description',
             'node_groups', 'anti_affinity', 'use_autoconfig', 'is_default',
             'is_protected', 'is_public', 'domain_name']


def _format_node_groups_list(node_groups):
    return ', '.join(
        ['%s:%s' % (ng['name'], ng['count']) for ng in node_groups])


def _format_ct_output(app, data):
    data['plugin_version'] = data.pop('hadoop_version')
    data['node_groups'] = _format_node_groups_list(data['node_groups'])
    data['anti_affinity'] = osc_utils.format_list(data['anti_affinity'])


def _configure_node_groups(app, node_groups, client):
    node_groups_list = dict(
        map(lambda x: x.split(':', 1), node_groups))

    node_groups = []
    plugins_versions = set()

    for name, count in node_groups_list.items():
        ng = utils.get_resource(client.node_group_templates, name)
        node_groups.append({'name': ng.name,
                            'count': int(count),
                            'node_group_template_id': ng.id})
        plugins_versions.add((ng.plugin_name, ng.hadoop_version))

    if len(plugins_versions) != 1:
        raise exceptions.CommandError('Node groups with the same plugins '
                                      'and versions must be specified')

    plugin, plugin_version = plugins_versions.pop()
    return plugin, plugin_version, node_groups


class CreateClusterTemplate(command.ShowOne):
    """Creates cluster template"""

    log = logging.getLogger(__name__ + ".CreateClusterTemplate")

    def get_parser(self, prog_name):
        parser = super(CreateClusterTemplate, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar="<name>",
            help="Name of the cluster template [REQUIRED if JSON is not "
                 "provided]",
        )
        parser.add_argument(
            '--node-groups',
            metavar="<node-group:instances_count>",
            nargs="+",
            help="List of the node groups(names or IDs) and numbers of "
                 "instances for each one of them [REQUIRED if JSON is not "
                 "provided]"
        )
        parser.add_argument(
            '--anti-affinity',
            metavar="<anti-affinity>",
            nargs="+",
            help="List of processes that should be added to an anti-affinity "
                 "group"
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help='Description of the cluster template'
        )
        parser.add_argument(
            '--autoconfig',
            action='store_true',
            default=False,
            help='If enabled, instances of the cluster will be '
                 'automatically configured',
        )
        parser.add_argument(
            '--public',
            action='store_true',
            default=False,
            help='Make the cluster template public (Visible from other '
                 'projects)',
        )
        parser.add_argument(
            '--protected',
            action='store_true',
            default=False,
            help='Make the cluster template protected',
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the cluster template. Other '
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
            help='JSON representation of the cluster template configs'
        )
        parser.add_argument(
            '--domain-name',
            metavar='<domain-name>',
            help='Domain name for instances of this cluster template. This '
                 'option is available if \'use_designate\' config is True'
        )
        return parser

    def _take_action(self, client, parsed_args):
        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = json.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))

            if 'neutron_management_network' in template:
                template['net_id'] = template.pop('neutron_management_network')

            data = client.cluster_templates.create(**template).to_dict()
        else:
            if not parsed_args.name or not parsed_args.node_groups:
                raise exceptions.CommandError(
                    'At least --name , --node-groups arguments should be '
                    'specified or json template should be provided with '
                    '--json argument')

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

            plugin, plugin_version, node_groups = (
                utils._cluster_templates_configure_ng(self.app,
                                                      parsed_args.node_groups,
                                                      client))
            data = utils.create_cluster_template(self.app, client, plugin,
                                                 plugin_version,
                                                 parsed_args, configs, shares,
                                                 node_groups)

        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_ct_output(self.app, data)
        data = utils.prepare_data(data, CT_FIELDS)

        return self.dict2columns(data)


class ListClusterTemplates(command.Lister):
    """Lists cluster templates"""

    log = logging.getLogger(__name__ + ".ListClusterTemplates")

    def get_parser(self, prog_name):
        parser = super(ListClusterTemplates, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--plugin',
            metavar="<plugin>",
            help="List cluster templates for specific plugin"
        )

        parser.add_argument(
            '--plugin-version',
            metavar="<plugin_version>",
            help="List cluster templates with specific version of the "
                 "plugin"
        )

        parser.add_argument(
            '--name',
            metavar="<name-substring>",
            help="List cluster templates with specific substring in the "
                 "name"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        search_opts = {}
        if parsed_args.plugin:
            search_opts['plugin_name'] = parsed_args.plugin
        if parsed_args.plugin_version:
            if utils.is_api_v2(self.app):
                search_opts['plugin_version'] = parsed_args.plugin_version
            else:
                search_opts['hadoop_version'] = parsed_args.plugin_version

        data = client.cluster_templates.list(search_opts=search_opts)

        if parsed_args.name:
            data = utils.get_by_name_substring(data, parsed_args.name)

        if parsed_args.long:
            columns = ('name', 'id', 'plugin_name', 'hadoop_version',
                       'node_groups', 'description')
            column_headers = utils.prepare_column_headers(
                columns, {'hadoop_version': 'plugin_version'})

        else:
            columns = ('name', 'id', 'plugin_name', 'hadoop_version')
            column_headers = utils.prepare_column_headers(
                columns, {'hadoop_version': 'plugin_version'})

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns,
                formatters={
                    'node_groups': _format_node_groups_list
                }
            ) for s in data)
        )


class ShowClusterTemplate(command.ShowOne):
    """Display cluster template details"""

    log = logging.getLogger(__name__ + ".ShowClusterTemplate")

    def get_parser(self, prog_name):
        parser = super(ShowClusterTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "cluster_template",
            metavar="<cluster-template>",
            help="Name or id of the cluster template to display",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = utils.get_resource(
            client.cluster_templates, parsed_args.cluster_template).to_dict()

        _format_ct_output(self.app, data)
        data = utils.prepare_data(data, CT_FIELDS)

        return self.dict2columns(data)


class DeleteClusterTemplate(command.Command):
    """Deletes cluster template"""

    log = logging.getLogger(__name__ + ".DeleteClusterTemplate")

    def get_parser(self, prog_name):
        parser = super(DeleteClusterTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "cluster_template",
            metavar="<cluster-template>",
            nargs="+",
            help="Name(s) or id(s) of the cluster template(s) to delete",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        for ct in parsed_args.cluster_template:
            ct_id = utils.get_resource_id(client.cluster_templates, ct)
            client.cluster_templates.delete(ct_id)
            sys.stdout.write(
                'Cluster template "{ct}" has been removed '
                'successfully.\n'.format(ct=ct))


class UpdateClusterTemplate(command.ShowOne):
    """Updates cluster template"""

    log = logging.getLogger(__name__ + ".UpdateClusterTemplate")

    def get_parser(self, prog_name):
        parser = super(UpdateClusterTemplate, self).get_parser(prog_name)

        parser.add_argument(
            'cluster_template',
            metavar="<cluster-template>",
            help="Name or ID of the cluster template [REQUIRED]",
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help="New name of the cluster template",
        )
        parser.add_argument(
            '--node-groups',
            metavar="<node-group:instances_count>",
            nargs="+",
            help="List of the node groups(names or IDs) and numbers of"
                 "instances for each one of them"
        )
        parser.add_argument(
            '--anti-affinity',
            metavar="<anti-affinity>",
            nargs="+",
            help="List of processes that should be added to an anti-affinity "
                 "group"
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help='Description of the cluster template'
        )
        autoconfig = parser.add_mutually_exclusive_group()
        autoconfig.add_argument(
            '--autoconfig-enable',
            action='store_true',
            help='Instances of the cluster will be '
                 'automatically configured',
            dest='use_autoconfig'
        )
        autoconfig.add_argument(
            '--autoconfig-disable',
            action='store_false',
            help='Instances of the cluster will not be '
                 'automatically configured',
            dest='use_autoconfig'
        )
        public = parser.add_mutually_exclusive_group()
        public.add_argument(
            '--public',
            action='store_true',
            help='Make the cluster template public '
                 '(Visible from other projects)',
            dest='is_public'
        )
        public.add_argument(
            '--private',
            action='store_false',
            help='Make the cluster template private '
                 '(Visible only from this tenant)',
            dest='is_public'
        )
        protected = parser.add_mutually_exclusive_group()
        protected.add_argument(
            '--protected',
            action='store_true',
            help='Make the cluster template protected',
            dest='is_protected'
        )
        protected.add_argument(
            '--unprotected',
            action='store_false',
            help='Make the cluster template unprotected',
            dest='is_protected'
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the cluster template. Other '
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
            help='JSON representation of the cluster template configs'
        )
        parser.add_argument(
            '--domain-name',
            metavar='<domain-name>',
            default=None,
            help='Domain name for instances of this cluster template. This '
                 'option is available if \'use_designate\' config is True'
        )
        parser.set_defaults(is_public=None, is_protected=None,
                            use_autoconfig=None)
        return parser

    def _take_action(self, client, parsed_args, ct_id):
        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = json.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))
            data = client.cluster_templates.update(
                ct_id, **template).to_dict()
        else:
            plugin, plugin_version, node_groups = None, None, None
            if parsed_args.node_groups:
                plugin, plugin_version, node_groups = (
                    utils._cluster_templates_configure_ng(
                        self.app, parsed_args.node_groups, client))

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

            data = utils.update_cluster_template(self.app, client, plugin,
                                                 plugin_version, parsed_args,
                                                 configs, shares, node_groups,
                                                 ct_id)

        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        ct_id = utils.get_resource_id(
            client.cluster_templates, parsed_args.cluster_template)

        data = self._take_action(client, parsed_args, ct_id)

        _format_ct_output(self.app, data)
        data = utils.prepare_data(data, CT_FIELDS)

        return self.dict2columns(data)


class ImportClusterTemplate(command.ShowOne):
    """Imports cluster template"""

    log = logging.getLogger(__name__ + ".ImportClusterTemplate")

    def get_parser(self, prog_name):
        parser = super(ImportClusterTemplate, self).get_parser(prog_name)

        parser.add_argument(
            'json',
            metavar="<json>",
            help="JSON containing cluster template",
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help="Name of the cluster template",
        )
        parser.add_argument(
            '--default-image-id',
            metavar="<default_image_id>",
            help="Default image ID to be used",
        )
        parser.add_argument(
            '--node-groups',
            metavar="<node-group:instances_count>",
            nargs="+",
            required=True,
            help="List of the node groups(names or IDs) and numbers of "
                 "instances for each one of them"
        )
        return parser

    def _take_action(self, client, parsed_args):
        if (not parsed_args.node_groups):
            raise exceptions.CommandError('--node_groups should be specified')

        blob = osc_utils.read_blob_file_contents(parsed_args.json)
        try:
            template = json.loads(blob)
        except ValueError as e:
            raise exceptions.CommandError(
                'An error occurred when reading '
                'template from file %s: %s' % (parsed_args.json, e))

        if parsed_args.default_image_id:
            template['cluster_template']['default_image_id'] = (
                parsed_args.default_image_id)
        else:
            template['cluster_template']['default_image_id'] = None

        if parsed_args.name:
            template['cluster_template']['name'] = parsed_args.name

        if 'neutron_management_network' in template['cluster_template']:
            template['cluster_template']['net_id'] = (
                template['cluster_template'].pop('neutron_management_network'))

        plugin, plugin_version, node_groups = (
            utils._cluster_templates_configure_ng_configure_node_groups(
                self.app, parsed_args.node_groups, client))
        if (('plugin_version' in template['cluster_template'] and
                template['cluster_template']['plugin_version'] !=
                plugin_version) or
                ('plugin' in template['cluster_template'] and
                    template['cluster_template']['plugin'] != plugin)):
            raise exceptions.CommandError(
                'Plugin of plugin version do not match between template '
                'and given node group templates')
        template['cluster_template']['node_groups'] = node_groups

        data = client.cluster_templates.create(
            **template['cluster_template']).to_dict()

        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_ct_output(self.app, data)
        data = utils.prepare_data(data, CT_FIELDS)

        return self.dict2columns(data)


class ExportClusterTemplate(command.Command):
    """Export cluster template to JSON"""

    log = logging.getLogger(__name__ + ".ExportClusterTemplate")

    def get_parser(self, prog_name):
        parser = super(ExportClusterTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "cluster_template",
            metavar="<cluster-template>",
            help="Name or id of the cluster template to export",
        )
        parser.add_argument(
            "--file",
            metavar="<filename>",
            help="Name of the file cluster template should be exported to "
                 "If not provided, print to stdout"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        ngt_id = utils.get_resource_id(
            client.cluster_templates, parsed_args.cluster_template)
        response = client.cluster_templates.export(ngt_id)
        result = json.dumps(response._info, indent=4)+"\n"
        if parsed_args.file:
            with open(parsed_args.file, "w+") as file:
                file.write(result)
        else:
            sys.stdout.write(result)
