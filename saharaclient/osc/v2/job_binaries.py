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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils as osc_utils
from oslo_log import log as logging
from oslo_serialization import jsonutils

from saharaclient.osc import utils
from saharaclient.osc.v1 import job_binaries as jb_v1


class CreateJobBinary(command.ShowOne):
    """Creates job binary"""

    log = logging.getLogger(__name__ + ".CreateJobBinary")

    def get_parser(self, prog_name):
        parser = super(CreateJobBinary, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar="<name>",
            help="Name of the job binary [REQUIRED if JSON is not provided]",
        )
        creation_type = parser.add_mutually_exclusive_group()
        creation_type.add_argument(
            '--url',
            metavar='<url>',
            help='URL for the job binary [REQUIRED if JSON and file are '
                 'not provided]'
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help="Description of the job binary"
        )
        username = parser.add_mutually_exclusive_group()
        username.add_argument(
            '--username',
            metavar='<username>',
            help='Username for accessing the job binary URL',
        )
        username.add_argument(
            '--access-key',
            metavar='<accesskey>',
            help='S3 access key for accessing the job binary URL',
        )
        password = parser.add_mutually_exclusive_group()
        password.add_argument(
            '--password',
            metavar='<password>',
            help='Password for accessing the job binary URL',
        )
        password.add_argument(
            '--secret-key',
            metavar='<secretkey>',
            help='S3 secret key for accessing the job binary URL',
        )
        password.add_argument(
            '--password-prompt',
            dest="password_prompt",
            action="store_true",
            help='Prompt interactively for password',
        )
        password.add_argument(
            '--secret-key-prompt',
            dest="secret_key_prompt",
            action="store_true",
            help='Prompt interactively for S3 secret key',
        )
        parser.add_argument(
            '--s3-endpoint',
            metavar='<endpoint>',
            help='S3 endpoint for accessing the job binary URL (ignored if '
                 'binary not in S3',
        )
        parser.add_argument(
            '--public',
            action='store_true',
            default=False,
            help='Make the job binary public',
        )
        parser.add_argument(
            '--protected',
            action='store_true',
            default=False,
            help='Make the job binary protected',
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the job binary. Other '
                 'arguments will not be taken into account if this one is '
                 'provided'
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
            data = client.job_binaries.create(**template).to_dict()
        else:
            if parsed_args.password_prompt:
                parsed_args.password = osc_utils.get_password(
                    self.app.stdin, confirm=False)

            if parsed_args.secret_key_prompt:
                parsed_args.secret_key = osc_utils.get_password(
                    self.app.stdin, confirm=False)

            if not parsed_args.password:
                parsed_args.password = parsed_args.secret_key

            if not parsed_args.username:
                parsed_args.username = parsed_args.access_key

            if parsed_args.password and not parsed_args.username:
                raise exceptions.CommandError(
                    'Username via --username, or S3 access key via '
                    '--access-key should be provided with password')

            if parsed_args.username and not parsed_args.password:
                raise exceptions.CommandError(
                    'Password should be provided via --password or '
                    '--secret-key, or entered interactively with '
                    '--password-prompt or --secret-key-prompt')

            if parsed_args.password and parsed_args.username:
                if not parsed_args.url:
                    raise exceptions.CommandError(
                        'URL must be provided via --url')
                if parsed_args.url.startswith('s3'):
                    if not parsed_args.s3_endpoint:
                        raise exceptions.CommandError(
                            'S3 job binaries need an endpoint provided via '
                            '--s3-endpoint')
                    extra = {
                        'accesskey': parsed_args.username,
                        'secretkey': parsed_args.password,
                        'endpoint': parsed_args.s3_endpoint,
                    }

                else:
                    extra = {
                        'user': parsed_args.username,
                        'password': parsed_args.password
                    }
            else:
                extra = None

            data = client.job_binaries.create(
                name=parsed_args.name, url=parsed_args.url,
                description=parsed_args.description, extra=extra,
                is_public=parsed_args.public,
                is_protected=parsed_args.protected).to_dict()

        data = utils.prepare_data(data, jb_v1.JOB_BINARY_FIELDS)

        return self.dict2columns(data)


class ListJobBinaries(jb_v1.ListJobBinaries):
    """Lists job binaries"""

    log = logging.getLogger(__name__ + ".ListJobBinaries")


class ShowJobBinary(jb_v1.ShowJobBinary):
    """Display job binary details"""

    log = logging.getLogger(__name__ + ".ShowJobBinary")


class DeleteJobBinary(jb_v1.DeleteJobBinary):
    """Deletes job binary"""

    log = logging.getLogger(__name__ + ".DeleteJobBinary")


class UpdateJobBinary(jb_v1.UpdateJobBinary):
    """Updates job binary"""

    log = logging.getLogger(__name__ + ".UpdateJobBinary")


class DownloadJobBinary(jb_v1.DownloadJobBinary):
    """Downloads job binary"""

    log = logging.getLogger(__name__ + ".DownloadJobBinary")
