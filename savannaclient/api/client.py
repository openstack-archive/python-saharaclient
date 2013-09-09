# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from keystoneclient.v2_0 import client as keystone_client

from savannaclient.openstack.common import log as logging

from savannaclient.api import cluster_templates
from savannaclient.api import clusters
from savannaclient.api import data_sources
from savannaclient.api import httpclient
from savannaclient.api import images
from savannaclient.api import job_binaries
from savannaclient.api import job_executions
from savannaclient.api import job_origins
from savannaclient.api import jobs
from savannaclient.api import node_group_templates
from savannaclient.api import plugins

LOG = logging.getLogger(__name__)


class Client(object):
    def __init__(self, username, api_key, project_id=None, project_name=None,
                 auth_url=None, savanna_url=None, timeout=None,
                 endpoint_type='publicURL', service_type='mapreduce',
                 input_auth_token=None):

        keystone = keystone_client.Client(username=username,
                                          password=api_key,
                                          token=input_auth_token,
                                          tenant_id=project_id,
                                          tenant_name=project_name,
                                          auth_url=auth_url,
                                          timeout=timeout)

        keystone.authenticate()
        token = keystone.auth_token
        if savanna_url:
            savanna_url = str(savanna_url) + "/" + str(project_id)
        else:
            catalog = keystone.service_catalog.get_endpoints(service_type)
            if service_type in catalog:
                for e_type, endpoint in catalog.get[service_type][0].items():
                    if str(e_type).lower() == str(endpoint_type).lower():
                        savanna_url = endpoint
                        break

        if not savanna_url:
            LOG.warning("Could not determine url for Savanna. "
                        "Trying localhost with default port.")
            savanna_url = "http://localhost:8386/v1.1/" + project_id

        self.client = httpclient.HTTPClient(savanna_url, token)

        self.clusters = clusters.ClusterManager(self)
        self.cluster_templates = cluster_templates.ClusterTemplateManager(self)
        self.node_group_templates = (node_group_templates.
                                     NodeGroupTemplateManager(self))
        self.plugins = plugins.PluginManager(self)
        self.images = images.ImageManager(self)

        self.data_sources = data_sources.DataSourceManager(self)
        self.jobs = jobs.JobsManager(self)
        self.job_origins = job_origins.JobOriginsManager(self)
        self.job_executions = job_executions.JobExecutionsManager(self)
        self.job_binaries = job_binaries.JobExecutionsManager(self)
