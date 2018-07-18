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
from saharaclient.osc.v1.job_templates import JOB_TYPES_CHOICES


class ListJobTypes(command.Lister):
    """Lists job types supported by plugins"""

    log = logging.getLogger(__name__ + ".ListJobTypes")

    def get_parser(self, prog_name):
        parser = super(ListJobTypes, self).get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar="<type>",
            choices=JOB_TYPES_CHOICES,
            help="Get information about specific job type"
        )
        parser.add_argument(
            '--plugin',
            metavar="<plugin>",
            help="Get only job types supported by this plugin"
        )
        parser.add_argument(
            '--plugin-version',
            metavar="<plugin_version>",
            help="Get only job types supported by specific version of the "
                 "plugin. This parameter will be taken into account only if "
                 "plugin is provided"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        search_opts = {}
        if parsed_args.type:
            search_opts['type'] = parsed_args.type
        if parsed_args.plugin:
            search_opts['plugin'] = parsed_args.plugin
            if parsed_args.plugin_version:
                search_opts['plugin_version'] = parsed_args.plugin_version
        elif parsed_args.plugin_version:
            raise exceptions.CommandError(
                '--plugin-version argument should be specified with --plugin '
                'argument')

        data = client.job_types.list(search_opts=search_opts)
        for job in data:
            plugins = []
            for plugin in job.plugins:
                versions = ", ".join(sorted(plugin["versions"].keys()))
                if versions:
                    versions = "(" + versions + ")"
                plugins.append(plugin["name"] + versions)
            job.plugins = ', '.join(plugins)

        columns = ('name', 'plugins')
        column_headers = utils.prepare_column_headers(columns)

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns
            ) for s in data)
        )


class GetJobTypeConfigs(command.Command):
    """Get job type configs"""

    log = logging.getLogger(__name__ + ".GetJobTypeConfigs")

    def get_parser(self, prog_name):
        parser = super(GetJobTypeConfigs, self).get_parser(prog_name)
        parser.add_argument(
            "job_type",
            metavar="<job-type>",
            choices=JOB_TYPES_CHOICES,
            help="Type of the job to provide config information about",
        )
        parser.add_argument(
            '--file',
            metavar="<file>",
            help='Destination file (defaults to job type)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        if not parsed_args.file:
            parsed_args.file = parsed_args.job_type

        data = client.jobs.get_configs(parsed_args.job_type).to_dict()

        if path.exists(parsed_args.file):
            self.log.error('File "%s" already exists. Choose another one with '
                           '--file argument.' % parsed_args.file)
        else:
            with open(parsed_args.file, 'w') as f:
                jsonutils.dump(data, f, indent=4)
            sys.stdout.write(
                '"%(type)s" job configs were saved in "%(file)s"'
                'file' % {'type': parsed_args.job_type,
                          'file': parsed_args.file})
