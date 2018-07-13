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
from oslo_serialization import jsonutils

from saharaclient.osc import utils

JOB_TEMPLATE_FIELDS = ['name', 'id', 'type', 'mains', 'libs', 'description',
                       'is_public', 'is_protected']

JOB_TYPES_CHOICES = ['Hive', 'Java', 'MapReduce', 'Storm', 'Storm.Pyleus',
                     'Pig', 'Shell', 'MapReduce.Streaming', 'Spark']


def _format_job_template_output(data):
    data['mains'] = osc_utils.format_list(
        ['%s:%s' % (m['name'], m['id']) for m in data['mains']])
    data['libs'] = osc_utils.format_list(
        ['%s:%s' % (l['name'], l['id']) for l in data['libs']])


class CreateJobTemplate(command.ShowOne):
    """Creates job template"""

    log = logging.getLogger(__name__ + ".CreateJobTemplate")

    def get_parser(self, prog_name):
        parser = super(CreateJobTemplate, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar="<name>",
            help="Name of the job template [REQUIRED if JSON is not provided]",
        )
        parser.add_argument(
            '--type',
            metavar="<type>",
            choices=JOB_TYPES_CHOICES,
            help="Type of the job (%s) "
                 "[REQUIRED if JSON is not provided]" % ', '.join(
                    JOB_TYPES_CHOICES)
        )
        parser.add_argument(
            '--mains',
            metavar="<main>",
            nargs='+',
            help="Name(s) or ID(s) for job's main job binary(s)",
        )
        parser.add_argument(
            '--libs',
            metavar="<lib>",
            nargs='+',
            help="Name(s) or ID(s) for job's lib job binary(s)",
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help="Description of the job template"
        )
        parser.add_argument(
            '--public',
            action='store_true',
            default=False,
            help='Make the job template public',
        )
        parser.add_argument(
            '--protected',
            action='store_true',
            default=False,
            help='Make the job template protected',
        )
        parser.add_argument(
            '--interface',
            metavar='<filename>',
            help='JSON representation of the interface'
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the job template'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = jsonutils.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))
            data = utils.create_job_template_json(self.app,
                                                  client, **template)
        else:
            if parsed_args.interface:
                blob = osc_utils.read_blob_file_contents(parsed_args.json)
                try:
                    parsed_args.interface = jsonutils.loads(blob)
                except ValueError as e:
                    raise exceptions.CommandError(
                        'An error occurred when reading '
                        'interface from file %s: %s' % (parsed_args.json, e))

            mains_ids = [utils.get_resource_id(client.job_binaries, m) for m
                         in parsed_args.mains] if parsed_args.mains else None
            libs_ids = [utils.get_resource_id(client.job_binaries, m) for m
                        in parsed_args.libs] if parsed_args.libs else None

            data = utils.create_job_templates(self.app, client, mains_ids,
                                              libs_ids, parsed_args)

        _format_job_template_output(data)
        data = utils.prepare_data(data, JOB_TEMPLATE_FIELDS)

        return self.dict2columns(data)


class ListJobTemplates(command.Lister):
    """Lists job templates"""

    log = logging.getLogger(__name__ + ".ListJobTemplates")

    def get_parser(self, prog_name):
        parser = super(ListJobTemplates, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--type',
            metavar="<type>",
            choices=JOB_TYPES_CHOICES,
            help="List job templates of specific type"
        )
        parser.add_argument(
            '--name',
            metavar="<name-substring>",
            help="List job templates with specific substring in the "
                 "name"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        search_opts = {'type': parsed_args.type} if parsed_args.type else {}

        data = utils.list_job_templates(self.app, client, search_opts)

        if parsed_args.name:
            data = utils.get_by_name_substring(data, parsed_args.name)

        if parsed_args.long:
            columns = ('name', 'id', 'type', 'description', 'is_public',
                       'is_protected')
            column_headers = utils.prepare_column_headers(columns)

        else:
            columns = ('name', 'id', 'type')
            column_headers = utils.prepare_column_headers(columns)

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns
            ) for s in data)
        )


class ShowJobTemplate(command.ShowOne):
    """Display job template details"""

    log = logging.getLogger(__name__ + ".ShowJobTemplate")

    def get_parser(self, prog_name):
        parser = super(ShowJobTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "job_template",
            metavar="<job-template>",
            help="Name or ID of the job template to display",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = utils.get_job_templates_resources(self.app, client, parsed_args)

        _format_job_template_output(data)
        data = utils.prepare_data(data, JOB_TEMPLATE_FIELDS)

        return self.dict2columns(data)


class DeleteJobTemplate(command.Command):
    """Deletes job template"""

    log = logging.getLogger(__name__ + ".DeleteJobTemplate")

    def get_parser(self, prog_name):
        parser = super(DeleteJobTemplate, self).get_parser(prog_name)
        parser.add_argument(
            "job_template",
            metavar="<job-template>",
            nargs="+",
            help="Name(s) or id(s) of the job template(s) to delete",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        for jt in parsed_args.job_template:
            utils.delete_job_templates(self.app, client, jt)
            sys.stdout.write(
                'Job template "{jt}" has been removed '
                'successfully.\n'.format(jt=jt))


class UpdateJobTemplate(command.ShowOne):
    """Updates job template"""

    log = logging.getLogger(__name__ + ".UpdateJobTemplate")

    def get_parser(self, prog_name):
        parser = super(UpdateJobTemplate, self).get_parser(prog_name)

        parser.add_argument(
            'job_template',
            metavar="<job-template>",
            help="Name or ID of the job template",
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help="New name of the job template",
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help='Description of the job template'
        )
        public = parser.add_mutually_exclusive_group()
        public.add_argument(
            '--public',
            action='store_true',
            help='Make the job template public '
                 '(Visible from other projects)',
            dest='is_public'
        )
        public.add_argument(
            '--private',
            action='store_false',
            help='Make the job_template private '
                 '(Visible only from this tenant)',
            dest='is_public'
        )
        protected = parser.add_mutually_exclusive_group()
        protected.add_argument(
            '--protected',
            action='store_true',
            help='Make the job template protected',
            dest='is_protected'
        )
        protected.add_argument(
            '--unprotected',
            action='store_false',
            help='Make the job template unprotected',
            dest='is_protected'
        )
        parser.set_defaults(is_public=None, is_protected=None)

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        jt_id = utils.get_job_template_id(self.app, client, parsed_args)

        update_data = utils.create_dict_from_kwargs(
            name=parsed_args.name,
            description=parsed_args.description,
            is_public=parsed_args.is_public,
            is_protected=parsed_args.is_protected
        )

        data = utils.update_job_templates(self.app, client, jt_id, update_data)

        _format_job_template_output(data)
        data = utils.prepare_data(data, JOB_TEMPLATE_FIELDS)

        return self.dict2columns(data)
