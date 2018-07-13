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

from saharaclient.osc.v1 import data_sources as ds_v1


class CreateDataSource(ds_v1.CreateDataSource):
    """Creates data source"""

    log = logging.getLogger(__name__ + ".CreateDataSource")


class ListDataSources(ds_v1.ListDataSources):
    """Lists data sources"""

    log = logging.getLogger(__name__ + ".ListDataSources")


class ShowDataSource(ds_v1.ShowDataSource):
    """Display data source details"""

    log = logging.getLogger(__name__ + ".ShowDataSource")


class DeleteDataSource(ds_v1.DeleteDataSource):
    """Delete data source"""

    log = logging.getLogger(__name__ + ".DeleteDataSource")


class UpdateDataSource(ds_v1.UpdateDataSource):
    """Update data source"""

    log = logging.getLogger(__name__ + ".UpdateDataSource")
