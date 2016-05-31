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

from cliff import command
from cliff import lister
from cliff import show
from openstackclient.common import utils as osc_utils
from oslo_log import log as logging
from oslo_serialization import jsonutils

from saharaclient.osc.v1 import utils


class ListPlugins(lister.Lister):
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
        self.log.debug("take_action(%s)" % parsed_args)
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


class ShowPlugin(show.ShowOne):
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
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.data_processing

        if parsed_args.plugin_version:
            data = client.plugins.get_version_details(
                parsed_args.plugin, parsed_args.plugin_version).to_dict()

            processes = data.pop('node_processes')
            for k, v in processes.items():
                processes[k] = osc_utils.format_list(v)
            data['required_image_tags'] = osc_utils.format_list(
                data['required_image_tags'])

            data = utils.prepare_data(
                data, ['required_image_tags', 'name', 'description', 'title'])

            data = zip(*sorted(data.items()) + [('', ''), (
                'Service:', 'Available processes:'), ('', '')] + sorted(
                processes.items()))
        else:
            data = client.plugins.get(parsed_args.plugin).to_dict()
            data['versions'] = osc_utils.format_list(data['versions'])
            data = utils.prepare_data(
                data, ['versions', 'name', 'description', 'title'])
            data = self.dict2columns(data)

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
            help='Destination file (defaults to plugin name)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.data_processing

        if not parsed_args.file:
            parsed_args.file = parsed_args.plugin

        data = client.plugins.get_version_details(
            parsed_args.plugin, parsed_args.plugin_version).to_dict()

        if path.exists(parsed_args.file):
            self.log.error('File "%s" already exists. Chose another one with '
                           '--file argument.' % parsed_args.file)
        else:
            with open(parsed_args.file, 'w') as f:
                jsonutils.dump(data, f, indent=4)
            sys.stdout.write(
                '"%(plugin)s" plugin configs was saved in "%(file)s"'
                'file' % {'plugin': parsed_args.plugin,
                          'file': parsed_args.file})
