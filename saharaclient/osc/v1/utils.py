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

import six
import time

from oslo_utils import timeutils
from oslo_utils import uuidutils

from saharaclient.api import base


def get_resource(manager, name_or_id):
    if uuidutils.is_uuid_like(name_or_id):
        return manager.get(name_or_id)
    else:
        return manager.find_unique(name=name_or_id)


def get_resource_id(manager, name_or_id):
    if uuidutils.is_uuid_like(name_or_id):
        return name_or_id
    else:
        return manager.find_unique(name=name_or_id).id


def create_dict_from_kwargs(**kwargs):
    return dict((k, v) for (k, v) in six.iteritems(kwargs) if v is not None)


def prepare_data(data, fields):
    new_data = {}
    for f in fields:
        if f in data:
            new_data[f.replace('_', ' ').capitalize()] = data[f]

    return new_data


def prepare_column_headers(columns, remap=None):
    remap = remap if remap else {}
    new_columns = []
    for c in columns:
        for old, new in remap.items():
            c = c.replace(old, new)
        new_columns.append(c.replace('_', ' ').capitalize())

    return new_columns


def get_by_name_substring(data, name):
    return [obj for obj in data if name in obj.name]


def wait_for_delete(manager, obj_id, sleep_time=5, timeout=3000):
    s_time = timeutils.utcnow()
    while timeutils.delta_seconds(s_time, timeutils.utcnow()) < timeout:
        try:
            manager.get(obj_id)
        except base.APIException as ex:
            if ex.error_code == 404:
                return True
            raise
        time.sleep(sleep_time)

    return False
