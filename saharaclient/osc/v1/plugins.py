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

from os import path
import sys

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from oslo_log import log as logging
from oslo_serialization import jsonutils

from saharaclient.osc import utils


def _serialize_label_items(plugin):
    labels = {}
    pl_labels = plugin.get('plugin_labels', {})
    for label, data in pl_labels.items():
        labels['plugin: %s' % label] = data['status']
    vr_labels = plugin.get('version_labels', {})
    for version, version_data in vr_labels.items():
        for label, data in version_data.items():
            labels[
                'plugin version %s: %s' % (version, label)] = data['status']
    labels = utils.prepare_data(labels, list(labels.keys()))
    return sorted(labels.items())


class ListPlugins(command.Lister):
    """Lists plugins"""

    log = logging.getLogger(__name__ + ".ListPlugins")

    def get_parser(self, prog_name):
        parser = super(ListPlugins, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        data = client.plugins.list()

        if parsed_args.long:
            columns = ('name', 'title', 'versions', 'description')
            column_headers = utils.prepare_column_headers(columns)

        else:
            columns = ('name', 'versions')
            column_headers = utils.prepare_column_headers(columns)

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns,
                formatters={
                    'versions': osc_utils.format_list
                },
            ) for s in data)
        )


class ShowPlugin(command.ShowOne):
    """Display plugin details"""

    log = logging.getLogger(__name__ + ".ShowPlugin")

    def get_parser(self, prog_name):
        parser = super(ShowPlugin, self).get_parser(prog_name)
        parser.add_argument(
            "plugin",
            metavar="<plugin>",
            help="Name of the plugin to display",
        )
        parser.add_argument(
            "--plugin-version",
            metavar="<plugin_version>",
            help='Version of the plugin to display'
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        if parsed_args.plugin_version:
            data = client.plugins.get_version_details(
                parsed_args.plugin, parsed_args.plugin_version).to_dict()

            processes = data.pop('node_processes')
            for k, v in processes.items():
                processes[k] = osc_utils.format_list(v)
            data['required_image_tags'] = osc_utils.format_list(
                data['required_image_tags'])
            label_items = _serialize_label_items(data)
            data = utils.prepare_data(
                data, ['required_image_tags', 'name', 'description', 'title'])
            data = self.dict2columns(data)
            data = utils.extend_columns(data, label_items)
            data = utils.extend_columns(
                data, [('Service:', 'Available processes:')])
            data = utils.extend_columns(
                data, sorted(processes.items()))
        else:
            data = client.plugins.get(parsed_args.plugin).to_dict()
            data['versions'] = osc_utils.format_list(data['versions'])
            items = _serialize_label_items(data)
            data = utils.prepare_data(
                data, ['versions', 'name', 'description', 'title'])
            data = utils.extend_columns(self.dict2columns(data), items)
        return data


class GetPluginConfigs(command.Command):
    """Get plugin configs"""

    log = logging.getLogger(__name__ + ".GetPluginConfigs")

    def get_parser(self, prog_name):
        parser = super(GetPluginConfigs, self).get_parser(prog_name)
        parser.add_argument(
            "plugin",
            metavar="<plugin>",
            help="Name of the plugin to provide config information about",
        )
        parser.add_argument(
            "plugin_version",
            metavar="<plugin_version>",
            help="Version of the plugin to provide config information about",
        )
        parser.add_argument(
            '--file',
            metavar="<file>",
            help="Destination file (defaults to a combination of "
                 "plugin name and plugin version)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        if not parsed_args.file:
            parsed_args.file = (parsed_args.plugin + '-' +
                                parsed_args.plugin_version)

        if path.exists(parsed_args.file):
            msg = ('File "%s" already exists. Choose another one with '
                   '--file argument.' % parsed_args.file)
            raise exceptions.CommandError(msg)
        else:
            data = client.plugins.get_version_details(
                parsed_args.plugin, parsed_args.plugin_version).to_dict()

            with open(parsed_args.file, 'w') as f:
                jsonutils.dump(data, f, indent=4)
            sys.stdout.write(
                '"%(plugin)s" plugin "%(version)s" version configs '
                'was saved in "%(file)s" file\n' % {
                    'plugin': parsed_args.plugin,
                    'version': parsed_args.plugin_version,
                    'file': parsed_args.file})


class UpdatePlugin(command.ShowOne):
    log = logging.getLogger(__name__ + ".UpdatePlugin")

    def get_parser(self, prog_name):
        parser = super(UpdatePlugin, self).get_parser(prog_name)
        parser.add_argument(
            "plugin",
            metavar="<plugin>",
            help="Name of the plugin to provide config information about",
        )
        parser.add_argument(
            'json',
            metavar="<json>",
            help='JSON representation of the plugin update dictionary',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        blob = osc_utils.read_blob_file_contents(parsed_args.json)
        try:
            update_dict = jsonutils.loads(blob)
        except ValueError as e:
            raise exceptions.CommandError(
                'An error occurred when reading '
                'update dict from file %s: %s' % (parsed_args.json, e))
        plugin = client.plugins.update(parsed_args.plugin, update_dict)
        data = plugin.to_dict()
        data['versions'] = osc_utils.format_list(data['versions'])
        items = _serialize_label_items(data)
        data = utils.prepare_data(
            data, ['versions', 'name', 'description', 'title'])
        data = utils.extend_columns(self.dict2columns(data), items)

        return data
