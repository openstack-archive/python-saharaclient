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
from saharaclient.osc.v1 import clusters as c_v1


def _format_cluster_output(app, data):
    data['image'] = data.pop('default_image_id')
    data['node_groups'] = c_v1._format_node_groups_list(data['node_groups'])
    data['anti_affinity'] = osc_utils.format_list(data['anti_affinity'])


class CreateCluster(c_v1.CreateCluster):
    """Creates cluster"""

    log = logging.getLogger(__name__ + ".CreateCluster")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        if parsed_args.count and parsed_args.count > 1:
            clusters = []
            for cluster in data['clusters']:
                clusters.append(
                    utils.get_resource(client.clusters,
                                       cluster['cluster']['id']))

            if parsed_args.wait:
                for cluster in clusters:
                    if not osc_utils.wait_for_status(
                            client.clusters.get, cluster.id):
                        self.log.error(
                            'Error occurred during cluster creation: %s',
                            data['id'])

            data = {}
            for cluster in clusters:
                data[cluster.name] = cluster.id

        else:
            if parsed_args.wait:
                if not osc_utils.wait_for_status(
                        client.clusters.get, data['id']):
                    self.log.error(
                        'Error occurred during cluster creation: %s',
                        data['id'])
                data = client.clusters.get(data['id']).to_dict()
            _format_cluster_output(self.app, data)
            data = utils.prepare_data(data, c_v1.CLUSTER_FIELDS)

        return self.dict2columns(data)


class ListClusters(c_v1.ListClusters):
    """Lists clusters"""

    log = logging.getLogger(__name__ + ".ListClusters")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        search_opts = {}
        if parsed_args.plugin:
            search_opts['plugin_name'] = parsed_args.plugin
        if parsed_args.plugin_version:
            search_opts['plugin_version'] = parsed_args.plugin_version

        data = client.clusters.list(search_opts=search_opts)

        if parsed_args.name:
            data = utils.get_by_name_substring(data, parsed_args.name)

        if parsed_args.long:
            columns = ('name', 'id', 'plugin_name', 'plugin_version',
                       'status', 'description', 'default_image_id')
            column_headers = utils.prepare_column_headers(
                columns, {'default_image_id': 'image'})
        else:
            columns = ('name', 'id', 'plugin_name', 'plugin_version',
                       'status')
            column_headers = utils.prepare_column_headers(
                columns, {'default_image_id': 'image'})

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns
            ) for s in data)
        )


class ShowCluster(c_v1.ShowCluster):
    """Display cluster details"""

    log = logging.getLogger(__name__ + ".ShowCluster")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data, provision_steps = self._take_action(client, parsed_args)

        _format_cluster_output(self.app, data)

        data = self._show_cluster_info(data, provision_steps, parsed_args)
        return data


class DeleteCluster(c_v1.DeleteCluster):
    """Deletes cluster"""

    log = logging.getLogger(__name__ + ".DeleteCluster")

    def get_parser(self, prog_name):
        parser = super(DeleteCluster, self).get_parser(prog_name)
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Force the deletion of the cluster',
        )
        return parser

    def _choose_delete_mode(self, parsed_args):
        if parsed_args.force:
            return "force_delete"
        else:
            return "delete"


class UpdateCluster(c_v1.UpdateCluster):
    """Updates cluster"""

    log = logging.getLogger(__name__ + ".UpdateCluster")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_cluster_output(self.app, data)
        data = utils.prepare_data(data, c_v1.CLUSTER_FIELDS)

        return self.dict2columns(data)


class ScaleCluster(c_v1.ScaleCluster):
    """Scales cluster"""

    log = logging.getLogger(__name__ + ".ScaleCluster")

    def _get_json_arg_helptext(self):
        return '''
               JSON representation of the cluster scale object. Other
               arguments (except for --wait) will not be taken into
               account if this one is provided. Specifiying a JSON
               object is also the only way to indicate specific
               instances to decomission.
               '''

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_cluster_output(self.app, data)
        data = utils.prepare_data(data, c_v1.CLUSTER_FIELDS)

        return self.dict2columns(data)


class VerificationUpdateCluster(c_v1.VerificationUpdateCluster):
    """Updates cluster verifications"""

    log = logging.getLogger(__name__ + ".VerificationUpdateCluster")


class UpdateKeypairCluster(command.ShowOne):
    """Reflects an updated keypair on the cluster"""

    log = logging.getLogger(__name__ + ".UpdateKeypairCluster")

    def get_parser(self, prog_name):
        parser = super(UpdateKeypairCluster, self).get_parser(prog_name)

        parser.add_argument(
            'cluster',
            metavar="<cluster>",
            help="Name or ID of the cluster",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        cluster_id = utils.get_resource_id(
            client.clusters, parsed_args.cluster)
        client.clusters.update_keypair(cluster_id)
        sys.stdout.write(
            'Cluster "{cluster}" keypair has been updated.\n'
            .format(cluster=parsed_args.cluster))
        return {}, {}
