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

from osc_lib import utils as osc_utils
from oslo_log import log as logging

from saharaclient.osc import utils
from saharaclient.osc.v1 import cluster_templates as ct_v1


def _format_ct_output(app, data):
    data['node_groups'] = ct_v1._format_node_groups_list(data['node_groups'])
    data['anti_affinity'] = osc_utils.format_list(data['anti_affinity'])


class CreateClusterTemplate(ct_v1.CreateClusterTemplate):
    """Creates cluster template"""

    log = logging.getLogger(__name__ + ".CreateClusterTemplate")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_ct_output(self.app, data)
        data = utils.prepare_data(data, ct_v1.CT_FIELDS)

        return self.dict2columns(data)


class ListClusterTemplates(ct_v1.ListClusterTemplates):
    """Lists cluster templates"""

    log = logging.getLogger(__name__ + ".ListClusterTemplates")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        search_opts = {}
        if parsed_args.plugin:
            search_opts['plugin_name'] = parsed_args.plugin
        if parsed_args.plugin_version:
            search_opts['plugin_version'] = parsed_args.plugin_version

        data = client.cluster_templates.list(search_opts=search_opts)

        if parsed_args.name:
            data = utils.get_by_name_substring(data, parsed_args.name)

        if parsed_args.long:
            columns = ('name', 'id', 'plugin_name', 'plugin_version',
                       'node_groups', 'description')
            column_headers = utils.prepare_column_headers(columns)

        else:
            columns = ('name', 'id', 'plugin_name', 'plugin_version')
            column_headers = utils.prepare_column_headers(columns)

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns,
                formatters={
                    'node_groups': ct_v1._format_node_groups_list
                }
            ) for s in data)
        )


class ShowClusterTemplate(ct_v1.ShowClusterTemplate):
    """Display cluster template details"""

    log = logging.getLogger(__name__ + ".ShowClusterTemplate")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = utils.get_resource(
            client.cluster_templates, parsed_args.cluster_template).to_dict()

        _format_ct_output(self.app, data)
        data = utils.prepare_data(data, ct_v1.CT_FIELDS)

        return self.dict2columns(data)


class DeleteClusterTemplate(ct_v1.DeleteClusterTemplate):
    """Deletes cluster template"""

    log = logging.getLogger(__name__ + ".DeleteClusterTemplate")


class UpdateClusterTemplate(ct_v1.UpdateClusterTemplate):
    """Updates cluster template"""

    log = logging.getLogger(__name__ + ".UpdateClusterTemplate")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        ct_id = utils.get_resource_id(
            client.cluster_templates, parsed_args.cluster_template)

        data = self._take_action(client, parsed_args, ct_id)

        _format_ct_output(self.app, data)
        data = utils.prepare_data(data, ct_v1.CT_FIELDS)

        return self.dict2columns(data)


class ImportClusterTemplate(ct_v1.ImportClusterTemplate):
    """Imports cluster template"""

    log = logging.getLogger(__name__ + ".ImportClusterTemplate")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_ct_output(self.app, data)
        data = utils.prepare_data(data, ct_v1.CT_FIELDS)

        return self.dict2columns(data)


class ExportClusterTemplate(ct_v1.ExportClusterTemplate):
    """Export cluster template to JSON"""

    log = logging.getLogger(__name__ + ".ExportClusterTemplate")
