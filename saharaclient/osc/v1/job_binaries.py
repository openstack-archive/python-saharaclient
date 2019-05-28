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

from saharaclient.api import base
from saharaclient.osc import utils

JOB_BINARY_FIELDS = ['name', 'id', 'url', 'description', 'is_public',
                     'is_protected']


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
            '--data',
            metavar='<file>',
            help='File that will be stored in the internal DB [REQUIRED if '
                 'JSON and URL are not provided]'
        )
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
            if parsed_args.data:
                data = open(parsed_args.data).read()
                jbi_id = client.job_binary_internals.create(
                    parsed_args.name, data).id
                parsed_args.url = 'internal-db://' + jbi_id

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

        data = utils.prepare_data(data, JOB_BINARY_FIELDS)

        return self.dict2columns(data)


class ListJobBinaries(command.Lister):
    """Lists job binaries"""

    log = logging.getLogger(__name__ + ".ListJobBinaries")

    def get_parser(self, prog_name):
        parser = super(ListJobBinaries, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--name',
            metavar="<name-substring>",
            help="List job binaries with specific substring in the "
                 "name"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = client.job_binaries.list()

        if parsed_args.name:
            data = utils.get_by_name_substring(data, parsed_args.name)

        if parsed_args.long:
            columns = ('name', 'id', 'url', 'description', 'is_public',
                       'is_protected')
            column_headers = utils.prepare_column_headers(columns)

        else:
            columns = ('name', 'id', 'url')
            column_headers = utils.prepare_column_headers(columns)

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns
            ) for s in data)
        )


class ShowJobBinary(command.ShowOne):
    """Display job binary details"""

    log = logging.getLogger(__name__ + ".ShowJobBinary")

    def get_parser(self, prog_name):
        parser = super(ShowJobBinary, self).get_parser(prog_name)
        parser.add_argument(
            "job_binary",
            metavar="<job-binary>",
            help="Name or ID of the job binary to display",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = utils.get_resource(
            client.job_binaries, parsed_args.job_binary).to_dict()

        data = utils.prepare_data(data, JOB_BINARY_FIELDS)

        return self.dict2columns(data)


class DeleteJobBinary(command.Command):
    """Deletes job binary"""

    log = logging.getLogger(__name__ + ".DeleteJobBinary")

    def get_parser(self, prog_name):
        parser = super(DeleteJobBinary, self).get_parser(prog_name)
        parser.add_argument(
            "job_binary",
            metavar="<job-binary>",
            nargs="+",
            help="Name(s) or id(s) of the job binary(ies) to delete",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        for jb in parsed_args.job_binary:
            jb = utils.get_resource(client.job_binaries, jb)
            if jb.url.startswith("internal-db"):
                jbi_id = jb.url.replace('internal-db://', '')
                try:
                    client.job_binary_internals.delete(jbi_id)
                except base.APIException as ex:
                    # check if job binary internal was already deleted for
                    # some reasons
                    if not ex.error_code == '404':
                        raise
            client.job_binaries.delete(jb.id)
            sys.stdout.write(
                'Job binary "{jb}" has been removed '
                'successfully.\n'.format(jb=jb))


class UpdateJobBinary(command.ShowOne):
    """Updates job binary"""

    log = logging.getLogger(__name__ + ".UpdateJobBinary")

    def get_parser(self, prog_name):
        parser = super(UpdateJobBinary, self).get_parser(prog_name)

        parser.add_argument(
            'job_binary',
            metavar="<job-binary>",
            help="Name or ID of the job binary",
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help="New name of the job binary",
        )
        parser.add_argument(
            '--url',
            metavar='<url>',
            help='URL for the job binary [Internal DB URL can not be updated]'
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help='Description of the job binary'
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
        public = parser.add_mutually_exclusive_group()
        public.add_argument(
            '--public',
            action='store_true',
            help='Make the job binary public (Visible from other projects)',
            dest='is_public'
        )
        public.add_argument(
            '--private',
            action='store_false',
            help='Make the job binary private (Visible only from'
                 ' this project)',
            dest='is_public'
        )
        protected = parser.add_mutually_exclusive_group()
        protected.add_argument(
            '--protected',
            action='store_true',
            help='Make the job binary protected',
            dest='is_protected'
        )
        protected.add_argument(
            '--unprotected',
            action='store_false',
            help='Make the job binary unprotected',
            dest='is_protected'
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the update object. Other '
                 'arguments will not be taken into account if this one is '
                 'provided'
        )
        parser.set_defaults(is_public=None, is_protected=None)

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        jb_id = utils.get_resource_id(
            client.job_binaries, parsed_args.job_binary)

        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = jsonutils.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))
            data = client.job_binaries.update(jb_id, template).to_dict()
        else:
            if parsed_args.password_prompt:
                parsed_args.password = osc_utils.get_password(
                    self.app.stdin, confirm=False)
            if parsed_args.secret_key_prompt:
                parsed_args.secret_key = osc_utils.get_password(
                    self.app.stdin, confirm=False)

            extra = {}
            if parsed_args.password:
                extra['password'] = parsed_args.password
            if parsed_args.username:
                extra['user'] = parsed_args.username
            if parsed_args.access_key:
                extra['accesskey'] = parsed_args.access_key
            if parsed_args.secret_key:
                extra['secretkey'] = parsed_args.secret_key
            if parsed_args.s3_endpoint:
                extra['endpoint'] = parsed_args.s3_endpoint
            if not extra:
                extra = None

            update_fields = utils.create_dict_from_kwargs(
                name=parsed_args.name, url=parsed_args.url,
                description=parsed_args.description,
                extra=extra, is_public=parsed_args.is_public,
                is_protected=parsed_args.is_protected
            )

            data = client.job_binaries.update(
                jb_id, update_fields).to_dict()

        data = utils.prepare_data(data, JOB_BINARY_FIELDS)

        return self.dict2columns(data)


class DownloadJobBinary(command.Command):
    """Downloads job binary"""

    log = logging.getLogger(__name__ + ".DownloadJobBinary")

    def get_parser(self, prog_name):
        parser = super(DownloadJobBinary, self).get_parser(prog_name)
        parser.add_argument(
            "job_binary",
            metavar="<job-binary>",
            help="Name or ID of the job binary to download",
        )
        parser.add_argument(
            '--file',
            metavar="<file>",
            help='Destination file (defaults to job binary name)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        if not parsed_args.file:
            parsed_args.file = parsed_args.job_binary

        if path.exists(parsed_args.file):
            msg = ('File "%s" already exists. Chose another one with '
                   '--file argument.' % parsed_args.file)
            raise exceptions.CommandError(msg)
        else:
            jb_id = utils.get_resource_id(
                client.job_binaries, parsed_args.job_binary)
            data = client.job_binaries.get_file(jb_id)

            with open(parsed_args.file, 'wb') as f:
                f.write(data)
            sys.stdout.write(
                'Job binary "{jb}" has been downloaded '
                'successfully.\n'.format(jb=parsed_args.job_binary))
