# Copyright (c) 2014 Mirantis Inc.
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

from oslo_utils import importutils


class UnsupportedVersion(Exception):
    """Indication for using an unsupported version of the API.

    Indicates that the user is trying to use an unsupported
    version of the API.
    """
    pass


def get_client_class(version):
    version_map = {
        '1.0': 'saharaclient.api.client.Client',
        '1.1': 'saharaclient.api.client.Client',
    }
    try:
        client_path = version_map[str(version)]
    except (KeyError, ValueError):
        supported_versions = ', '.join(version_map.keys())
        msg = ("Invalid client version '%(version)s'; must be one of: "
               "%(versions)s") % {'version': version,
                                  'versions': supported_versions}
        raise UnsupportedVersion(msg)

    return importutils.import_class(client_path)


def Client(version, *args, **kwargs):
    client_class = get_client_class(version)
    return client_class(*args, **kwargs)
