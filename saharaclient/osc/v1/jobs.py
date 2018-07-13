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

JOB_FIELDS = ['id', 'job_template_id', 'cluster_id', 'input_id', 'output_id',
              'start_time', 'end_time', 'status', 'is_public', 'is_protected',
              'engine_job_id']

JOB_STATUS_CHOICES = ['done-with-error', 'failed', 'killed', 'pending',
                      'running', 'succeeded', 'to-be-killed']


def _format_job_output(app, data):
    data['status'] = data['info']['status']
    del data['info']
    data['job_template_id'] = data.pop('job_id')


class ExecuteJob(command.ShowOne):
    """Executes job"""

    log = logging.getLogger(__name__ + ".ExecuteJob")

    def get_parser(self, prog_name):
        parser = super(ExecuteJob, self).get_parser(prog_name)

        parser.add_argument(
            '--job-template',
            metavar="<job-template>",
            help="Name or ID of the job template "
                 "[REQUIRED if JSON is not provided]",
        )
        parser.add_argument(
            '--cluster',
            metavar="<cluster>",
            help="Name or ID of the cluster "
                 "[REQUIRED if JSON is not provided]",
        )
        parser.add_argument(
            '--input',
            metavar="<input>",
            help="Name or ID of the input data source",
        )
        parser.add_argument(
            '--output',
            metavar="<output>",
            help="Name or ID of the output data source",
        )
        parser.add_argument(
            '--params',
            metavar="<name:value>",
            nargs='+',
            help="Parameters to add to the job"
        )
        parser.add_argument(
            '--args',
            metavar="<argument>",
            nargs='+',
            help="Arguments to add to the job"
        )
        parser.add_argument(
            '--public',
            action='store_true',
            default=False,
            help='Make the job public',
        )
        parser.add_argument(
            '--protected',
            action='store_true',
            default=False,
            help='Make the job protected',
        )
        configs = parser.add_mutually_exclusive_group()
        configs.add_argument(
            '--config-json',
            metavar='<filename>',
            help='JSON representation of the job configs'
        )
        configs.add_argument(
            '--configs',
            metavar="<name:value>",
            nargs='+',
            help="Configs to add to the job"
        )
        parser.add_argument(
            '--interface',
            metavar='<filename>',
            help='JSON representation of the interface'
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the job. Other arguments will not be '
                 'taken into account if this one is provided'
        )
        return parser

    def _take_action(self, client, parsed_args):

        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = jsonutils.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))

            if 'job_configs' in template:
                template['configs'] = template.pop('job_configs')

            data = utils.create_job_json(client, self.app, template)
        else:
            if not parsed_args.cluster or not parsed_args.job_template:
                raise exceptions.CommandError(
                    'At least --cluster, --job-template, arguments should be '
                    'specified or json template should be provided with '
                    '--json argument')

            job_configs = {}

            if parsed_args.interface:
                blob = osc_utils.read_blob_file_contents(parsed_args.json)
                try:
                    parsed_args.interface = jsonutils.loads(blob)
                except ValueError as e:
                    raise exceptions.CommandError(
                        'An error occurred when reading '
                        'interface from file %s: %s' % (parsed_args.json, e))

            if parsed_args.config_json:
                blob = osc_utils.read_blob_file_contents(parsed_args.configs)
                try:
                    job_configs['configs'] = jsonutils.loads(blob)
                except ValueError as e:
                    raise exceptions.CommandError(
                        'An error occurred when reading '
                        'configs from file %s: %s' % (parsed_args.json, e))
            elif parsed_args.configs:
                job_configs['configs'] = dict(
                    map(lambda x: x.split(':', 1), parsed_args.configs))

            if parsed_args.args:
                job_configs['args'] = parsed_args.args

            if parsed_args.params:
                job_configs['params'] = dict(
                    map(lambda x: x.split(':', 1), parsed_args.params))

            jt_id = utils.get_job_template_id(self.app, client, parsed_args)
            cluster_id = utils.get_resource_id(
                client.clusters, parsed_args.cluster)
            if parsed_args.input not in [None, "", "None"]:
                input_id = utils.get_resource_id(
                    client.data_sources, parsed_args.input)
            else:
                input_id = None
            if parsed_args.output not in [None, "", "None"]:
                output_id = utils.get_resource_id(
                    client.data_sources, parsed_args.output)
            else:
                output_id = None

            data = utils.create_job(client, self.app, jt_id, cluster_id,
                                    input_id, output_id, job_configs,
                                    parsed_args)
        sys.stdout.write(
            'Job "{job}" has been started successfully.\n'.format(
                job=data['id']))

        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_job_output(self.app, data)
        data = utils.prepare_data(data, JOB_FIELDS)

        return self.dict2columns(data)


class ListJobs(command.Lister):
    """Lists jobs"""

    log = logging.getLogger(__name__ + ".ListJobs")

    def get_parser(self, prog_name):
        parser = super(ListJobs, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--status',
            metavar="<status>",
            choices=JOB_STATUS_CHOICES,
            help="List jobs with specific status"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = client.job_executions.list()

        for job in data:
            job.status = job.info['status']

        if parsed_args.status:
            data = [job for job in data
                    if job.info['status'] == parsed_args.status.replace(
                        '-', '').upper()]

        if parsed_args.long:
            columns = ('id', 'cluster id', 'job id', 'status', 'start time',
                       'end time')
            column_headers = utils.prepare_column_headers(columns)

        else:
            columns = ('id', 'cluster id', 'job id', 'status')
            column_headers = utils.prepare_column_headers(columns)

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns
            ) for s in data)
        )


class ShowJob(command.ShowOne):
    """Display job details"""

    log = logging.getLogger(__name__ + ".ShowJob")

    def get_parser(self, prog_name):
        parser = super(ShowJob, self).get_parser(prog_name)
        parser.add_argument(
            "job",
            metavar="<job>",
            help="ID of the job to display",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = client.job_executions.get(parsed_args.job).to_dict()

        _format_job_output(self.app, data)
        data = utils.prepare_data(data, JOB_FIELDS)

        return self.dict2columns(data)


class DeleteJob(command.Command):
    """Deletes job"""

    log = logging.getLogger(__name__ + ".DeleteJob")

    def get_parser(self, prog_name):
        parser = super(DeleteJob, self).get_parser(prog_name)
        parser.add_argument(
            "job",
            metavar="<job>",
            nargs="+",
            help="ID(s) of the job(s) to delete",
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help='Wait for the job(s) delete to complete',
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        for job_id in parsed_args.job:
            client.job_executions.delete(job_id)

            sys.stdout.write(
                'Job "{job}" deletion has been started.\n'.format(job=job_id))

        if parsed_args.wait:
            for job_id in parsed_args.job:
                wait_for_delete = utils.wait_for_delete(
                    client.job_executions, job_id)

                if not wait_for_delete:
                    self.log.error(
                        'Error occurred during job deleting: %s' %
                        job_id)
                else:
                    sys.stdout.write(
                        'Job "{job}" has been removed successfully.\n'.format(
                            job=job_id))


class UpdateJob(command.ShowOne):
    """Updates job"""

    log = logging.getLogger(__name__ + ".UpdateJob")

    def get_parser(self, prog_name):
        parser = super(UpdateJob, self).get_parser(prog_name)

        parser.add_argument(
            'job',
            metavar="<job>",
            help="ID of the job to update",
        )
        public = parser.add_mutually_exclusive_group()
        public.add_argument(
            '--public',
            action='store_true',
            help='Make the job public (Visible from other projects)',
            dest='is_public'
        )
        public.add_argument(
            '--private',
            action='store_false',
            help='Make the job private (Visible only from this project)',
            dest='is_public'
        )
        protected = parser.add_mutually_exclusive_group()
        protected.add_argument(
            '--protected',
            action='store_true',
            help='Make the job protected',
            dest='is_protected'
        )
        protected.add_argument(
            '--unprotected',
            action='store_false',
            help='Make the job unprotected',
            dest='is_protected'
        )

        parser.set_defaults(is_public=None, is_protected=None)

        return parser

    def _take_action(self, client, parsed_args):
        update_dict = utils.create_dict_from_kwargs(
            is_public=parsed_args.is_public,
            is_protected=parsed_args.is_protected)

        data = utils.update_job(client, self.app, parsed_args, update_dict)

        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_job_output(self.app, data)
        data = utils.prepare_data(data, JOB_FIELDS)

        return self.dict2columns(data)
