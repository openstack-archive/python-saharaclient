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


class Parameter(object):
    """This bean is used for building config entries."""
    def __init__(self, config):
        self.name = config['name']
        self.description = config.get('description', "No description")
        self.required = not config['is_optional']
        self.default_value = config.get('default_value', None)
        self.initial_value = self.default_value
        self.param_type = config['config_type']
        self.priority = int(config.get('priority', 2))
