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

"""OpenStackClient plugin for Data Processing service."""

from osc_lib import utils
from oslo_log import log as logging

LOG = logging.getLogger(__name__)

DEFAULT_DATA_PROCESSING_API_VERSION = "1.1"
API_VERSION_OPTION = "os_data_processing_api_version"
API_NAME = "data_processing"
API_VERSIONS = {
    "1.1": "saharaclient.api.client.Client",
    "2": "saharaclient.api.client.ClientV2"
}


def make_client(instance):
    data_processing_client = utils.get_client_class(
        API_NAME,
        instance._api_version[API_NAME],
        API_VERSIONS)
    LOG.debug('Instantiating data-processing client: %s',
              data_processing_client)

    kwargs = utils.build_kwargs_dict('endpoint_type', instance._interface)

    client = data_processing_client(
        session=instance.session,
        region_name=instance._region_name,
        sahara_url=instance._cli_options.data_processing_url,
        **kwargs
        )
    return client


def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument(
        "--os-data-processing-api-version",
        metavar="<data-processing-api-version>",
        default=utils.env(
            'OS_DATA_PROCESSING_API_VERSION',
            default=DEFAULT_DATA_PROCESSING_API_VERSION),
        help=("Data processing API version, default=" +
              DEFAULT_DATA_PROCESSING_API_VERSION +
              ' (Env: OS_DATA_PROCESSING_API_VERSION)'))
    parser.add_argument(
        "--os-data-processing-url",
        default=utils.env(
            "OS_DATA_PROCESSING_URL"),
        help=("Data processing API URL, "
              "(Env: OS_DATA_PROCESSING_API_URL)"))
    return parser
