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

from saharaclient.osc.v1 import job_templates as jt_v1


class CreateJobTemplate(jt_v1.CreateJobTemplate):
    """Creates job template"""

    log = logging.getLogger(__name__ + ".CreateJobTemplate")


class ListJobTemplates(jt_v1.ListJobTemplates):
    """Lists job templates"""

    log = logging.getLogger(__name__ + ".ListJobTemplates")


class ShowJobTemplate(jt_v1.ShowJobTemplate):
    """Display job template details"""

    log = logging.getLogger(__name__ + ".ShowJobTemplate")


class DeleteJobTemplate(jt_v1.DeleteJobTemplate):
    """Deletes job template"""

    log = logging.getLogger(__name__ + ".DeleteJobTemplate")


class UpdateJobTemplate(jt_v1.UpdateJobTemplate):
    """Updates job template"""

    log = logging.getLogger(__name__ + ".UpdateJobTemplate")
