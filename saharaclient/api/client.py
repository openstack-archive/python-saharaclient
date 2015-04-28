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

import warnings

from keystoneclient import adapter
from keystoneclient.auth.identity import v2
from keystoneclient.auth.identity import v3
from keystoneclient.auth import token_endpoint
from keystoneclient import exceptions
from keystoneclient import session as keystone_session
from keystoneclient.v2_0 import client as keystone_client_v2

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


USER_AGENT = 'python-saharaclient'


class HTTPClient(adapter.Adapter):

    def request(self, *args, **kwargs):
        kwargs.setdefault('raise_exc', False)
        return super(HTTPClient, self).request(*args, **kwargs)


class Client(object):
    def __init__(self, username=None, api_key=None, project_id=None,
                 project_name=None, auth_url=None, sahara_url=None,
                 endpoint_type='publicURL', service_type='data-processing',
                 input_auth_token=None, session=None, auth=None,
                 insecure=False, cacert=None, region_name=None, **kwargs):

        if not session:
            warnings.warn('Passing authentication parameters to saharaclient '
                          'is deprecated. Please construct and pass an '
                          'authenticated session object directly.',
                          DeprecationWarning)

            if input_auth_token:
                auth = token_endpoint.Token(sahara_url, input_auth_token)

            else:
                auth = self._get_keystone_auth(auth_url=auth_url,
                                               username=username,
                                               api_key=api_key,
                                               project_id=project_id,
                                               project_name=project_name)

            verify = True
            if insecure:
                verify = False
            elif cacert:
                verify = cacert

            session = keystone_session.Session(verify=verify)

        if not auth:
            auth = session.auth

        service_type = self._determine_service_type(session,
                                                    auth,
                                                    service_type,
                                                    endpoint_type)

        kwargs['user_agent'] = USER_AGENT
        kwargs.setdefault('interface', endpoint_type)
        kwargs.setdefault('endpoint_override', sahara_url)

        client = HTTPClient(session=session,
                            auth=auth,
                            service_type=service_type,
                            region_name=region_name,
                            **kwargs)

        self.clusters = clusters.ClusterManager(client)
        self.cluster_templates = (
            cluster_templates.ClusterTemplateManager(client)
        )
        self.node_group_templates = (
            node_group_templates.NodeGroupTemplateManager(client)
        )
        self.plugins = plugins.PluginManager(client)
        self.images = images.ImageManager(client)

        self.data_sources = data_sources.DataSourceManager(client)
        self.jobs = jobs.JobsManager(client)
        self.job_executions = job_executions.JobExecutionsManager(client)
        self.job_binaries = job_binaries.JobBinariesManager(client)
        self.job_binary_internals = (
            job_binary_internals.JobBinaryInternalsManager(client)
        )
        self.job_types = job_types.JobTypesManager(client)

    def _get_keystone_auth(self, username=None, api_key=None, auth_url=None,
                           project_id=None, project_name=None):
        if not auth_url:
            raise RuntimeError("No auth url specified")

        if 'v2.0' in auth_url:
            return v2.Password(auth_url=auth_url,
                               username=username,
                               password=api_key,
                               tenant_id=project_id,
                               tenant_name=project_name)
        else:
            # NOTE(jamielennox): Setting these to default is what
            # keystoneclient does in the event they are not passed.
            return v3.Password(auth_url=auth_url,
                               username=username,
                               password=api_key,
                               user_domain_id='default',
                               project_id=project_id,
                               project_name=project_name,
                               project_domain_id='default')

    @staticmethod
    def _determine_service_type(session, auth, service_type, interface):
        """Check a catalog for data-processing or data_processing"""

        # NOTE(jamielennox): calling get_endpoint forces an auth on
        # initialization which is required for backwards compatibility. It
        # also allows us to reset the service type if not in the catalog.
        for st in (service_type, service_type.replace('-', '_')):
            try:
                url = auth.get_endpoint(session,
                                        service_type=st,
                                        interface=interface)
            except exceptions.Unauthorized:
                raise RuntimeError("Not Authorized")
            except exceptions.EndpointNotFound:
                # NOTE(jamielennox): bug #1428447. This should not be
                # raised, instead None should be returned. Handle in case
                # it changes in the future
                url = None

            if url:
                return st

        raise RuntimeError("Could not find Sahara endpoint in catalog")

    @staticmethod
    def get_projects_list(keystone_client):
        if isinstance(keystone_client, keystone_client_v2.Client):
            return keystone_client.tenants

        return keystone_client.projects
