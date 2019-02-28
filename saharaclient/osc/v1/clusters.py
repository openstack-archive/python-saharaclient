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

CLUSTER_FIELDS = ["cluster_template_id", "use_autoconfig", "user_keypair_id",
                  "status", "image", "node_groups", "id", "info",
                  "anti_affinity", "plugin_version", "name", "is_transient",
                  "is_protected", "description", "is_public",
                  "neutron_management_network", "plugin_name"]


def _format_node_groups_list(node_groups):
    return ', '.join(
        ['%s:%s' % (ng['name'], ng['count']) for ng in node_groups])


def _format_cluster_output(app, data):
    data['plugin_version'] = data.pop('hadoop_version')
    data['image'] = data.pop('default_image_id')
    data['node_groups'] = _format_node_groups_list(data['node_groups'])
    data['anti_affinity'] = osc_utils.format_list(data['anti_affinity'])


def _prepare_health_checks(data):
    additional_data = {}
    ver = data.get('verification', {})
    additional_fields = ['verification_status']
    additional_data['verification_status'] = ver.get('status', 'UNKNOWN')
    for check in ver.get('checks', []):
        row_name = "Health check (%s)" % check['name']
        additional_data[row_name] = check['status']
        additional_fields.append(row_name)
    return additional_data, additional_fields


class CreateCluster(command.ShowOne):
    """Creates cluster"""

    log = logging.getLogger(__name__ + ".CreateCluster")

    def get_parser(self, prog_name):
        parser = super(CreateCluster, self).get_parser(prog_name)

        parser.add_argument(
            '--name',
            metavar="<name>",
            help="Name of the cluster [REQUIRED if JSON is not provided]",
        )
        parser.add_argument(
            '--cluster-template',
            metavar="<cluster-template>",
            help="Cluster template name or ID [REQUIRED if JSON is not "
                 "provided]"
        )
        parser.add_argument(
            '--image',
            metavar="<image>",
            help='Image that will be used for cluster deployment (Name or ID) '
                 '[REQUIRED if JSON is not provided]'
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help='Description of the cluster'
        )
        parser.add_argument(
            '--user-keypair',
            metavar="<keypair>",
            help='User keypair to get acces to VMs after cluster creation'
        )
        parser.add_argument(
            '--neutron-network',
            metavar="<network>",
            help='Instances of the cluster will get fixed IP addresses in '
                 'this network. (Name or ID should be provided)'
        )
        parser.add_argument(
            '--count',
            metavar="<count>",
            type=int,
            help='Number of clusters to be created'
        )
        parser.add_argument(
            '--public',
            action='store_true',
            default=False,
            help='Make the cluster public (Visible from other projects)',
        )
        parser.add_argument(
            '--protected',
            action='store_true',
            default=False,
            help='Make the cluster protected',
        )
        parser.add_argument(
            '--transient',
            action='store_true',
            default=False,
            help='Create transient cluster',
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help='JSON representation of the cluster. Other '
                 'arguments (except for --wait) will not be taken into '
                 'account if this one is provided'
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help='Wait for the cluster creation to complete',
        )

        return parser

    def _take_action(self, client, parsed_args):
        network_client = self.app.client_manager.network

        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = jsonutils.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))

            if 'neutron_management_network' in template:
                template['net_id'] = template.pop('neutron_management_network')

            if 'count' in template:
                parsed_args.count = template['count']

            data = client.clusters.create(**template).to_dict()
        else:
            if not parsed_args.name or not parsed_args.cluster_template \
                    or not parsed_args.image:
                raise exceptions.CommandError(
                    'At least --name , --cluster-template, --image arguments '
                    'should be specified or json template should be provided '
                    'with --json argument')

            plugin, plugin_version, template_id = utils._get_plugin_version(
                self.app, parsed_args.cluster_template, client)

            image_id = utils.get_resource_id(client.images, parsed_args.image)

            net_id = (network_client.find_network(
                parsed_args.neutron_network, ignore_missing=False).id if
                parsed_args.neutron_network else None)

            data = utils.create_cluster(client, self.app, parsed_args, plugin,
                                        plugin_version, template_id, image_id,
                                        net_id)
        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        if parsed_args.count and parsed_args.count > 1:
            clusters = [
                utils.get_resource(client.clusters, id)
                for id in data['clusters']]

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
            data = utils.prepare_data(data, CLUSTER_FIELDS)

        return self.dict2columns(data)


class ListClusters(command.Lister):
    """Lists clusters"""

    log = logging.getLogger(__name__ + ".ListClusters")

    def get_parser(self, prog_name):
        parser = super(ListClusters, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--plugin',
            metavar="<plugin>",
            help="List clusters with specific plugin"
        )

        parser.add_argument(
            '--plugin-version',
            metavar="<plugin_version>",
            help="List clusters with specific version of the "
                 "plugin"
        )

        parser.add_argument(
            '--name',
            metavar="<name-substring>",
            help="List clusters with specific substring in the name"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        search_opts = {}
        if parsed_args.plugin:
            search_opts['plugin_name'] = parsed_args.plugin
        if parsed_args.plugin_version:
            search_opts['hadoop_version'] = parsed_args.plugin_version

        data = client.clusters.list(search_opts=search_opts)

        if parsed_args.name:
            data = utils.get_by_name_substring(data, parsed_args.name)

        if parsed_args.long:
            columns = ('name', 'id', 'plugin_name', 'hadoop_version',
                       'status', 'description', 'default_image_id')
            column_headers = utils.prepare_column_headers(
                columns, {'hadoop_version': 'plugin_version',
                          'default_image_id': 'image'})
        else:
            columns = ('name', 'id', 'plugin_name', 'hadoop_version',
                       'status')
            column_headers = utils.prepare_column_headers(
                columns, {'hadoop_version': 'plugin_version',
                          'default_image_id': 'image'})

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns
            ) for s in data)
        )


class ShowCluster(command.ShowOne):
    """Display cluster details"""

    log = logging.getLogger(__name__ + ".ShowCluster")

    def get_parser(self, prog_name):
        parser = super(ShowCluster, self).get_parser(prog_name)
        parser.add_argument(
            "cluster",
            metavar="<cluster>",
            help="Name or id of the cluster to display",
        )
        parser.add_argument(
            '--verification',
            action='store_true',
            default=False,
            help='List additional fields for verifications',
        )

        parser.add_argument(
            '--show-progress',
            action='store_true',
            default=False,
            help='Provides ability to show brief details of event logs.'
        )

        parser.add_argument(
            '--full-dump-events',
            action='store_true',
            default=False,
            help='Provides ability to make full dump with event log details.'
        )
        return parser

    def _take_action(self, client, parsed_args):
        kwargs = {}
        if parsed_args.show_progress or parsed_args.full_dump_events:
            kwargs['show_progress'] = True
        data = utils.get_resource(
            client.clusters, parsed_args.cluster, **kwargs).to_dict()
        provision_steps = data.get('provision_progress', [])
        provision_steps = utils.created_at_sorted(provision_steps)

        if parsed_args.full_dump_events:
            file_name = utils.random_name('event-logs')
            # making full dump
            with open(file_name, 'w') as file:
                jsonutils.dump(provision_steps, file, indent=4)
            sys.stdout.write('Event log dump saved to file: %s\n' % file_name)
        return data, provision_steps

    def _show_cluster_info(self, data, provision_steps, parsed_args):
        fields = []
        if parsed_args.verification:
            ver_data, fields = _prepare_health_checks(data)
            data.update(ver_data)
        fields.extend(CLUSTER_FIELDS)

        data = self.dict2columns(utils.prepare_data(data, fields))

        if parsed_args.show_progress:
            output_steps = []
            for step in provision_steps:
                st_name, st_type = step['step_name'], step['step_type']
                description = "%s: %s" % (st_type, st_name)
                if step['successful'] is None:
                    progress = "Step in progress"
                elif step['successful']:
                    progress = "Step completed successfully"
                else:
                    progress = 'Step has failed events'
                output_steps += [(description, progress)]
            data = utils.extend_columns(data, output_steps)

        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data, provision_steps = self._take_action(client, parsed_args)

        _format_cluster_output(self.app, data)

        data = self._show_cluster_info(data, provision_steps, parsed_args)
        return data


class DeleteCluster(command.Command):
    """Deletes cluster"""

    log = logging.getLogger(__name__ + ".DeleteCluster")

    def get_parser(self, prog_name):
        parser = super(DeleteCluster, self).get_parser(prog_name)
        parser.add_argument(
            "cluster",
            metavar="<cluster>",
            nargs="+",
            help="Name(s) or id(s) of the cluster(s) to delete",
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help='Wait for the cluster(s) delete to complete',
        )

        return parser

    def _choose_delete_mode(self, parsed_args):
        return "delete"

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        delete_function_attr = self._choose_delete_mode(parsed_args)

        clusters = []
        for cluster in parsed_args.cluster:
            cluster_id = utils.get_resource_id(
                client.clusters, cluster)
            getattr(client.clusters, delete_function_attr)(cluster_id)
            clusters.append((cluster_id, cluster))
            sys.stdout.write(
                'Cluster "{cluster}" deletion has been started.\n'.format(
                    cluster=cluster))
        if parsed_args.wait:
            for cluster_id, cluster_arg in clusters:
                if not utils.wait_for_delete(client.clusters, cluster_id):
                    self.log.error(
                        'Error occurred during cluster deleting: %s' %
                        cluster_id)
                else:
                    sys.stdout.write(
                        'Cluster "{cluster}" has been removed '
                        'successfully.\n'.format(cluster=cluster_arg))


class UpdateCluster(command.ShowOne):
    """Updates cluster"""

    log = logging.getLogger(__name__ + ".UpdateCluster")

    def get_parser(self, prog_name):
        parser = super(UpdateCluster, self).get_parser(prog_name)

        parser.add_argument(
            'cluster',
            metavar="<cluster>",
            help="Name or ID of the cluster",
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            help="New name of the cluster",
        )
        parser.add_argument(
            '--description',
            metavar="<description>",
            help='Description of the cluster'
        )
        parser.add_argument(
            '--shares',
            metavar="<filename>",
            help='JSON representation of the manila shares'
        )
        public = parser.add_mutually_exclusive_group()
        public.add_argument(
            '--public',
            action='store_true',
            help='Make the cluster public '
                 '(Visible from other projects)',
            dest='is_public'
        )
        public.add_argument(
            '--private',
            action='store_false',
            help='Make the cluster private '
                 '(Visible only from this tenant)',
            dest='is_public'
        )
        protected = parser.add_mutually_exclusive_group()
        protected.add_argument(
            '--protected',
            action='store_true',
            help='Make the cluster protected',
            dest='is_protected'
        )
        protected.add_argument(
            '--unprotected',
            action='store_false',
            help='Make the cluster unprotected',
            dest='is_protected'
        )
        parser.set_defaults(is_public=None, is_protected=None)

        return parser

    def _take_action(self, client, parsed_args):
        cluster_id = utils.get_resource_id(
            client.clusters, parsed_args.cluster)

        shares = None
        if parsed_args.shares:
            blob = osc_utils.read_blob_file_contents(parsed_args.shares)
            try:
                shares = jsonutils.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'shares from file %s: %s' % (parsed_args.shares, e))

        update_dict = utils.create_dict_from_kwargs(
            name=parsed_args.name,
            description=parsed_args.description,
            is_public=parsed_args.is_public,
            is_protected=parsed_args.is_protected,
            shares=shares
        )
        data = client.clusters.update(cluster_id, **update_dict).cluster
        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_cluster_output(self.app, data)
        data = utils.prepare_data(data, CLUSTER_FIELDS)

        return self.dict2columns(data)


class ScaleCluster(command.ShowOne):
    """Scales cluster"""

    log = logging.getLogger(__name__ + ".ScaleCluster")

    def _get_json_arg_helptext(self):
        return '''
               JSON representation of the cluster scale object. Other
               arguments (except for --wait) will not be taken into
               account if this one is provided
               '''

    def get_parser(self, prog_name):
        parser = super(ScaleCluster, self).get_parser(prog_name)

        parser.add_argument(
            'cluster',
            metavar="<cluster>",
            help="Name or ID of the cluster",
        )
        parser.add_argument(
            '--instances',
            nargs='+',
            metavar='<node-group-template:instances_count>',
            help='Node group templates and number of their instances to be '
                 'scale to [REQUIRED if JSON is not provided]'
        )
        parser.add_argument(
            '--json',
            metavar='<filename>',
            help=self._get_json_arg_helptext()
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help='Wait for the cluster scale to complete',
        )

        return parser

    def _take_action(self, client, parsed_args):
        cluster = utils.get_resource(
            client.clusters, parsed_args.cluster)

        if parsed_args.json:
            blob = osc_utils.read_blob_file_contents(parsed_args.json)
            try:
                template = jsonutils.loads(blob)
            except ValueError as e:
                raise exceptions.CommandError(
                    'An error occurred when reading '
                    'template from file %s: %s' % (parsed_args.json, e))

            data = client.clusters.scale(cluster.id, template).cluster
        else:
            scale_object = {
                "add_node_groups": [],
                "resize_node_groups": []
            }
            scale_node_groups = dict(
                map(lambda x: x.split(':', 1), parsed_args.instances))
            cluster_ng_map = {
                ng['node_group_template_id']: ng['name'] for ng
                in cluster.node_groups}
            for name, count in scale_node_groups.items():
                ngt = utils.get_resource(client.node_group_templates, name)
                if ngt.id in cluster_ng_map:
                    scale_object["resize_node_groups"].append({
                        "name": cluster_ng_map[ngt.id],
                        "count": int(count)
                    })
                else:
                    scale_object["add_node_groups"].append({
                        "node_group_template_id": ngt.id,
                        "name": ngt.name,
                        "count": int(count)
                    })
            if not scale_object['add_node_groups']:
                del scale_object['add_node_groups']
            if not scale_object['resize_node_groups']:
                del scale_object['resize_node_groups']

            data = client.clusters.scale(cluster.id, scale_object).cluster

        sys.stdout.write(
            'Cluster "{cluster}" scaling has been started.\n'.format(
                cluster=parsed_args.cluster))
        if parsed_args.wait:
            if not osc_utils.wait_for_status(
                    client.clusters.get, data['id']):
                self.log.error(
                    'Error occurred during cluster scaling: %s' %
                    cluster.id)
            data = client.clusters.get(cluster.id).cluster

        return data

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_cluster_output(self.app, data)
        data = utils.prepare_data(data, CLUSTER_FIELDS)

        return self.dict2columns(data)


class VerificationUpdateCluster(command.ShowOne):
    """Updates cluster verifications"""

    log = logging.getLogger(__name__ + ".VerificationUpdateCluster")

    def get_parser(self, prog_name):
        parser = super(VerificationUpdateCluster, self).get_parser(prog_name)

        parser.add_argument(
            'cluster',
            metavar="<cluster>",
            help="Name or ID of the cluster",
        )
        status = parser.add_mutually_exclusive_group(required=True)
        status.add_argument(
            '--start',
            action='store_const',
            const='START',
            help='Start health verification for the cluster',
            dest='status'
        )
        status.add_argument(
            '--show',
            help='Show health of the cluster',
            action='store_true'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        if parsed_args.show:
            data = utils.get_resource(
                client.clusters, parsed_args.cluster).to_dict()
            ver_data, ver_fields = _prepare_health_checks(data)
            data = utils.prepare_data(ver_data, ver_fields)
            return self.dict2columns(data)
        else:
            cluster_id = utils.get_resource_id(
                client.clusters, parsed_args.cluster)
            client.clusters.verification_update(
                cluster_id, parsed_args.status)
            if parsed_args.status == 'START':
                print_status = 'started'
            sys.stdout.write(
                'Cluster "{cluster}" health verification has been '
                '{status}.\n'.format(cluster=parsed_args.cluster,
                                     status=print_status))

            return {}, {}
