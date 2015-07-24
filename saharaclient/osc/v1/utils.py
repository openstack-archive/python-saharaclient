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

from openstackclient.common import exceptions
from openstackclient.common import utils


def get_resource(manager, name_or_id):
    resource = utils.find_resource(manager, name_or_id)
    if isinstance(resource, list):
        if not resource:
            msg = "No %s with a name or ID of '%s' exists." % \
                (manager.resource_class.__name__.lower(), name_or_id)
            raise exceptions.CommandError(msg)
        if len(resource) > 1:
            msg = "More than one %s exists with the name '%s'." % \
                (manager.resource_class.__name__.lower(), name_or_id)
            raise exceptions.CommandError(msg)
        return resource[0]

    else:
        return resource


def prepare_data(data, fields):
    new_data = {}
    for f in fields:
        if f in data:
            new_data[f.replace('_', ' ').capitalize()] = data[f]

    return new_data
