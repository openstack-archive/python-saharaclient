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

import copy

from oslo_serialization import jsonutils
from six.moves.urllib import parse

from saharaclient._i18n import _


class Resource(object):
    resource_name = 'Something'
    defaults = {}

    def __init__(self, manager, info):
        self.manager = manager
        info = info.copy()
        self._info = info
        self._set_defaults(info)
        self._add_details(info)

    def _set_defaults(self, info):
        for name, value in self.defaults.items():
            if name not in info:
                info[name] = value

    def _add_details(self, info):
        for (k, v) in info.items():
            try:
                setattr(self, k, v)
                self._info[k] = v
            except AttributeError:
                # In this case we already defined the attribute on the class
                pass

    def to_dict(self):
        return copy.deepcopy(self._info)

    def __str__(self):
        return '%s %s' % (self.resource_name, str(self._info))


def _check_items(obj, searches):
    try:
        return all(getattr(obj, attr) == value for (attr, value) in searches)
    except AttributeError:
        return False


class NotUpdated(object):
    """A sentinel class to signal that parameter should not be updated."""
    def __repr__(self):
        return 'NotUpdated'


class ResourceManager(object):
    resource_class = None

    def __init__(self, api):
        self.api = api

    def find(self, **kwargs):
        return [i for i in self.list() if _check_items(i, kwargs.items())]

    def find_unique(self, **kwargs):
        found = self.find(**kwargs)
        if not found:
            raise APIException(error_code=404,
                               error_message=_("No matches found."))
        if len(found) > 1:
            raise APIException(error_code=409,
                               error_message=_("Multiple matches found."))
        return found[0]

    def _copy_if_defined(self, data, **kwargs):
        for var_name, var_value in kwargs.items():
            if var_value is not None:
                data[var_name] = var_value

    def _copy_if_updated(self, data, **kwargs):
        for var_name, var_value in kwargs.items():
            if not isinstance(var_value, NotUpdated):
                data[var_name] = var_value

    def _create(self, url, data, response_key=None, dump_json=True):
        if dump_json:
            kwargs = {'json': data}
        else:
            kwargs = {'data': data}

        resp = self.api.post(url, **kwargs)

        if resp.status_code != 202:
            self._raise_api_exception(resp)

        if response_key is not None:
            data = get_json(resp)[response_key]
        else:
            data = get_json(resp)
        return self.resource_class(self, data)

    def _update(self, url, data, response_key=None, dump_json=True):
        if dump_json:
            kwargs = {'json': data}
        else:
            kwargs = {'data': data}

        resp = self.api.put(url, **kwargs)

        if resp.status_code not in [200, 202]:
            self._raise_api_exception(resp)
        if response_key is not None:
            data = get_json(resp)[response_key]
        else:
            data = get_json(resp)

        return self.resource_class(self, data)

    def _patch(self, url, data, response_key=None, dump_json=True):
        if dump_json:
            kwargs = {'json': data}
        else:
            kwargs = {'data': data}

        resp = self.api.patch(url, **kwargs)

        if resp.status_code != 202:
            self._raise_api_exception(resp)
        if response_key is not None:
            data = get_json(resp)[response_key]
        else:
            data = get_json(resp)

        return self.resource_class(self, data)

    def _post(self, url, data, response_key=None, dump_json=True):
        if dump_json:
            kwargs = {'json': data}
        else:
            kwargs = {'data': data}

        resp = self.api.post(url, **kwargs)

        if resp.status_code != 202:
            self._raise_api_exception(resp)

        if response_key is not None:
            data = get_json(resp)[response_key]
        else:
            data = get_json(resp)

        return self.resource_class(self, data)

    def _list(self, url, response_key):
        resp = self.api.get(url)
        if resp.status_code == 200:
            data = get_json(resp)[response_key]

            return [self.resource_class(self, res)
                    for res in data]
        else:
            self._raise_api_exception(resp)

    def _page(self, url, response_key, limit=None):
        resp = self.api.get(url)
        if resp.status_code == 200:
            result = get_json(resp)
            data = result[response_key]
            meta = result.get('markers')

            next, prev = None, None

            if meta:
                prev = meta.get('prev')
                next = meta.get('next')

            l = [self.resource_class(self, res)
                 for res in data]

            return Page(l, prev, next, limit)
        else:
            self._raise_api_exception(resp)

    def _get(self, url, response_key=None):
        resp = self.api.get(url)

        if resp.status_code == 200:
            if response_key is not None:
                data = get_json(resp)[response_key]
            else:
                data = get_json(resp)
            return self.resource_class(self, data)
        else:
            self._raise_api_exception(resp)

    def _delete(self, url, data=None):
        if data is not None:
            kwargs = {'json': data}
            resp = self.api.delete(url, **kwargs)
        else:
            resp = self.api.delete(url)

        if resp.status_code not in [200, 204]:
            self._raise_api_exception(resp)

        if resp.status_code == 200:
            return get_json(resp)

    def _plurify_resource_name(self):
        return self.resource_class.resource_name + 's'

    def _raise_api_exception(self, resp):
        try:
            error_data = get_json(resp)
        except Exception:
            msg = _("Failed to parse response from Sahara: %s") % resp.reason
            raise APIException(
                error_code=resp.status_code,
                error_message=msg)

        raise APIException(error_code=error_data.get("error_code"),
                           error_name=error_data.get("error_name"),
                           error_message=error_data.get("error_message"))


def get_json(response):
    """Provide backward compatibility with old versions of requests library."""

    json_field_or_function = getattr(response, 'json', None)
    if callable(json_field_or_function):
        return response.json()
    else:
        return jsonutils.loads(response.content)


class APIException(Exception):
    def __init__(self, error_code=None, error_name=None, error_message=None):
        super(APIException, self).__init__(error_message)
        self.error_code = error_code
        self.error_name = error_name
        self.error_message = error_message


def get_query_string(search_opts, limit=None, marker=None, sort_by=None,
                     reverse=None):
    opts = {}
    if marker is not None:
        opts['marker'] = marker
    if limit is not None:
        opts['limit'] = limit
    if sort_by is not None:
        if reverse:
            opts['sort_by'] = "-%s" % sort_by
        else:
            opts['sort_by'] = sort_by
    if search_opts is not None:
        opts.update(search_opts)
    if opts:
        qparams = sorted(opts.items(), key=lambda x: x[0])
        query_string = "?%s" % parse.urlencode(qparams, doseq=True)
    else:
        query_string = ""
    return query_string


class Page(list):
    def __init__(self, l, prev, next, limit):
        super(Page, self).__init__(l)
        self.prev = prev
        self.next = next
        self.limit = limit
