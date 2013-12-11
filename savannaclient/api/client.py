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

from keystoneclient.v2_0 import client as keystone_client_v2
from keystoneclient.v3 import client as keystone_client_v3

from savannaclient.api import cluster_templates
from savannaclient.api import clusters
from savannaclient.api import data_sources
from savannaclient.api import httpclient
from savannaclient.api import images
from savannaclient.api import job_binaries
from savannaclient.api import job_binary_internals
from savannaclient.api import job_executions
from savannaclient.api import jobs
from savannaclient.api import node_group_templates
from savannaclient.api import plugins


class Client(object):
    def __init__(self, username=None, api_key=None, project_id=None,
                 project_name=None, auth_url=None, savanna_url=None,
                 endpoint_type='publicURL', service_type='data_processing',
                 input_auth_token=None):

        if not input_auth_token:
            keystone = self.get_keystone_client(username=username,
                                                api_key=api_key,
                                                auth_url=auth_url,
                                                project_id=project_id,
                                                project_name=project_name)
            input_auth_token = keystone.auth_token
        if not input_auth_token:
            raise RuntimeError("Not Authorized")

        savanna_catalog_url = savanna_url
        if not savanna_url:
            keystone = self.get_keystone_client(username=username,
                                                api_key=api_key,
                                                auth_url=auth_url,
                                                token=input_auth_token,
                                                project_id=project_id,
                                                project_name=project_name)
            catalog = keystone.service_catalog.get_endpoints(service_type)
            if service_type in catalog:
                for e_type, endpoint in catalog.get(service_type)[0].items():
                    if str(e_type).lower() == str(endpoint_type).lower():
                        savanna_catalog_url = endpoint
                        break
        if not savanna_catalog_url:
            raise RuntimeError("Could not find Savanna endpoint in catalog")

        if not project_id:
            keystone = self.get_keystone_client(username=username,
                                                api_key=api_key,
                                                auth_url=auth_url,
                                                token=input_auth_token,
                                                project_name=project_name)
            project_id = self.get_projects_list(keystone).find(
                name=project_name).id
            if not project_id:
                raise RuntimeError("Could not determine tenant id")

        savanna_url = savanna_catalog_url + "/" + project_id

        self.client = httpclient.HTTPClient(savanna_url, input_auth_token)

        self.clusters = clusters.ClusterManager(self)
        self.cluster_templates = cluster_templates.ClusterTemplateManager(self)
        self.node_group_templates = (node_group_templates.
                                     NodeGroupTemplateManager(self))
        self.plugins = plugins.PluginManager(self)
        self.images = images.ImageManager(self)

        self.data_sources = data_sources.DataSourceManager(self)
        self.jobs = jobs.JobsManager(self)
        self.job_executions = job_executions.JobExecutionsManager(self)
        self.job_binaries = job_binaries.JobBinariesManager(self)
        self.job_binary_internals =\
            job_binary_internals.JobBinaryInternalsManager(self)

    def get_keystone_client(self, username=None, api_key=None, auth_url=None,
                            token=None, project_id=None, project_name=None):
        if not auth_url:
                raise RuntimeError("No auth url specified")
        imported_client = keystone_client_v2 if "v2.0" in auth_url\
            else keystone_client_v3
        if not getattr(self, "keystone_client", None):
            self.keystone_client = imported_client.Client(
                username=username,
                password=api_key,
                token=token,
                tenant_id=project_id,
                tenant_name=project_name,
                auth_url=auth_url,
                endpoint=auth_url)

        self.keystone_client.authenticate()

        return self.keystone_client

    @staticmethod
    def get_projects_list(keystone_client):
        if isinstance(keystone_client, keystone_client_v2.Client):
            return keystone_client.tenants

        return keystone_client.projects
