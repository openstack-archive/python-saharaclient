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

from keystoneauth1 import adapter

from saharaclient.api import cluster_templates
from saharaclient.api import clusters
from saharaclient.api import data_sources
from saharaclient.api import images
from saharaclient.api import job_binaries
from saharaclient.api import job_binary_internals
from saharaclient.api import job_executions
from saharaclient.api import job_types
from saharaclient.api import jobs
from saharaclient.api import node_group_templates
from saharaclient.api import plugins
from saharaclient.api.v2 import job_templates
from saharaclient.api.v2 import jobs as jobs_v2


USER_AGENT = 'python-saharaclient'


class HTTPClient(adapter.Adapter):

    def request(self, *args, **kwargs):
        kwargs.setdefault('raise_exc', False)
        kwargs.setdefault('allow', {'allow_experimental': True})
        return super(HTTPClient, self).request(*args, **kwargs)


class Client(object):

    _api_version = '1.1'

    """Client for the OpenStack Data Processing API.
        :param session: Keystone session object. Required.
        :param string sahara_url: Endpoint override.
        :param string endpoint_type: Desired Sahara endpoint type.
        :param string service_type: Sahara service name in Keystone catalog.
        :param string region_name: Name of a region to select when choosing an
                                   endpoint from the service catalog.
    """
    def __init__(self, session=None, sahara_url=None,
                 endpoint_type='publicURL', service_type='data-processing',
                 region_name=None, **kwargs):

        if not session:
            raise RuntimeError("Must provide session")

        auth = session.auth

        kwargs['user_agent'] = USER_AGENT
        kwargs.setdefault('interface', endpoint_type)
        kwargs.setdefault('endpoint_override', sahara_url)

        client = HTTPClient(session=session,
                            auth=auth,
                            service_type=service_type,
                            region_name=region_name,
                            version=self._api_version,
                            **kwargs)

        self._register_managers(client)

    def _register_managers(self, client):
        self.clusters = clusters.ClusterManagerV1(client)
        self.cluster_templates = (
            cluster_templates.ClusterTemplateManagerV1(client)
        )
        self.node_group_templates = (
            node_group_templates.NodeGroupTemplateManagerV1(client)
        )
        self.plugins = plugins.PluginManagerV1(client)
        self.images = images.ImageManagerV1(client)
        self.data_sources = data_sources.DataSourceManagerV1(client)
        self.jobs = jobs.JobsManagerV1(client)
        self.job_executions = job_executions.JobExecutionsManager(client)
        self.job_binaries = job_binaries.JobBinariesManagerV1(client)
        self.job_binary_internals = (
            job_binary_internals.JobBinaryInternalsManager(client)
        )
        self.job_types = job_types.JobTypesManager(client)


class ClientV2(Client):

    _api_version = '2'

    def _register_managers(self, client):
        self.clusters = clusters.ClusterManagerV2(client)
        self.cluster_templates = (
            cluster_templates.ClusterTemplateManagerV2(client)
        )
        self.node_group_templates = (
            node_group_templates.NodeGroupTemplateManagerV2(client)
        )
        self.plugins = plugins.PluginManagerV2(client)
        self.images = images.ImageManagerV2(client)
        self.data_sources = data_sources.DataSourceManagerV2(client)
        self.job_templates = job_templates.JobTemplatesManagerV2(client)
        self.jobs = jobs_v2.JobsManagerV2(client)
        self.job_binaries = job_binaries.JobBinariesManagerV2(client)
        self.job_types = job_types.JobTypesManager(client)
