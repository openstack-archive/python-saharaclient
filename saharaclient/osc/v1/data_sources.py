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

from cliff import command
from cliff import lister
from cliff import show
from openstackclient.common import utils as osc_utils
from oslo_log import log as logging

from saharaclient.osc.v1 import utils


class CreateDataSource(show.ShowOne):
    """Creates data source"""

    log = logging.getLogger(__name__ + ".CreateDataSource")

    def get_parser(self, prog_name):
        parser = super(CreateDataSource, self).get_parser(prog_name)

        parser.add_argument(
            'name',
            metavar="<name>",
            help="Name of the data source",
        )
        parser.add_argument(
            '--type',
            metavar="<type>",
            choices=["swift", "hdfs", "maprfs"],
            help="Type of the data source (swift, hdfs or maprfs) [REQUIRED]",
            required=True
        )
        parser.add_argument(
            '--url',
            metavar="<url>",
            help="Url for the data source [REQUIRED]",
            required=True
        )
        parser.add_argument(
            '--username',
            metavar="<username>",
            help="Username for accessing the data source url"
        )
        parser.add_argument(
            '--password',
            metavar="<password>",
            help="Password for accessing the data source url"
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help="Description of the data source"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.data_processing

        description = parsed_args.description or ''
        data = client.data_sources.create(
            name=parsed_args.name, description=description,
            data_source_type=parsed_args.type, url=parsed_args.url,
            credential_user=parsed_args.username,
            credential_pass=parsed_args.password).to_dict()

        fields = ['name', 'id', 'type', 'url', 'description']
        data = utils.prepare_data(data, fields)

        return self.dict2columns(data)


class ListDataSources(lister.Lister):
    """Lists data sources"""

    log = logging.getLogger(__name__ + ".ListDataSources")

    def get_parser(self, prog_name):
        parser = super(ListDataSources, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--type',
            metavar="<type>",
            choices=["swift", "hdfs", "maprfs"],
            help="List data sources of specific type (swift, hdfs or maprfs)"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.data_processing
        search_opts = {'type': parsed_args.type} if parsed_args.type else {}

        data = client.data_sources.list(search_opts=search_opts)

        if parsed_args.long:
            columns = ('name', 'id', 'type', 'url', 'description')
            column_headers = [c.capitalize() for c in columns]

        else:
            columns = ('name', 'id', 'type')
            column_headers = [c.capitalize() for c in columns]

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns
            ) for s in data)
        )


class ShowDataSource(show.ShowOne):
    """Display data source details"""

    log = logging.getLogger(__name__ + ".ShowDataSource")

    def get_parser(self, prog_name):
        parser = super(ShowDataSource, self).get_parser(prog_name)
        parser.add_argument(
            "data_source",
            metavar="<data-source>",
            help="Name or id of the data source to display",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.data_processing

        data = utils.get_resource(
            client.data_sources, parsed_args.data_source).to_dict()

        fields = ['name', 'id', 'type', 'url', 'description']
        data = utils.prepare_data(data, fields)

        return self.dict2columns(data)


class DeleteDataSource(command.Command):
    """Delete data source"""

    log = logging.getLogger(__name__ + ".DeleteDataSource")

    def get_parser(self, prog_name):
        parser = super(DeleteDataSource, self).get_parser(prog_name)
        parser.add_argument(
            "data_source",
            metavar="<data-source>",
            help="Name or id of the data source to delete",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        client = self.app.client_manager.data_processing
        data_source_id = utils.get_resource(
            client.data_sources, parsed_args.data_source).id
        client.data_sources.delete(data_source_id)
