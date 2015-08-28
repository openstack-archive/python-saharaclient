# Copyright (c) 2013 Mirantis Inc.
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

from six.moves.urllib import parse

from saharaclient.api import base


class Cluster(base.Resource):
    resource_name = 'Cluster'


class ClusterManager(base.ResourceManager):
    resource_class = Cluster

    def create(self, name, plugin_name, hadoop_version,
               cluster_template_id=None, default_image_id=None,
               is_transient=None, description=None, cluster_configs=None,
               node_groups=None, user_keypair_id=None,
               anti_affinity=None, net_id=None, count=None,
               use_autoconfig=None, shares=None,
               is_public=None, is_protected=None):

        data = {
            'name': name,
            'plugin_name': plugin_name,
            'hadoop_version': hadoop_version,
        }

        # Checking if count is greater than 1, otherwise we set it to None
        # so the created dict in the _copy_if_defined method does not contain
        # the count parameter.
        if count and count <= 1:
            count = None

        self._copy_if_defined(data,
                              cluster_template_id=cluster_template_id,
                              is_transient=is_transient,
                              default_image_id=default_image_id,
                              description=description,
                              cluster_configs=cluster_configs,
                              node_groups=node_groups,
                              user_keypair_id=user_keypair_id,
                              anti_affinity=anti_affinity,
                              neutron_management_network=net_id,
                              count=count,
                              use_autoconfig=use_autoconfig,
                              shares=shares,
                              is_public=is_public,
                              is_protected=is_protected)

        if count:
            return self._create('/clusters/multiple', data)

        return self._create('/clusters', data, 'cluster')

    def scale(self, cluster_id, scale_object):
        return self._update('/clusters/%s' % cluster_id, scale_object)

    def list(self, search_opts=None):
        query = base.get_query_string(search_opts)
        return self._list('/clusters%s' % query, 'clusters')

    def get(self, cluster_id, show_progress=False):
        url = ('/clusters/%(cluster_id)s?%(params)s' %
               {"cluster_id": cluster_id,
                "params": parse.urlencode({"show_progress": show_progress})})

        return self._get(url, 'cluster')

    def delete(self, cluster_id):
        self._delete('/clusters/%s' % cluster_id)

    def update(self, cluster_id, name=None, description=None, is_public=None,
               is_protected=None):

        data = {}
        self._copy_if_defined(data, name=name, description=description,
                              is_public=is_public, is_protected=is_protected)

        return self._patch('/clusters/%s' % cluster_id, data)
