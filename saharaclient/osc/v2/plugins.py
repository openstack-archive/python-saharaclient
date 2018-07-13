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

from oslo_log import log as logging

from saharaclient.osc.v1 import plugins as p_v1


class ListPlugins(p_v1.ListPlugins):
    """Lists plugins"""

    log = logging.getLogger(__name__ + ".ListPlugins")


class ShowPlugin(p_v1.ShowPlugin):
    """Display plugin details"""

    log = logging.getLogger(__name__ + ".ShowPlugin")


class GetPluginConfigs(p_v1.GetPluginConfigs):
    """Get plugin configs"""

    log = logging.getLogger(__name__ + ".GetPluginConfigs")


class UpdatePlugin(p_v1.UpdatePlugin):
    log = logging.getLogger(__name__ + ".UpdatePlugin")
