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

from os import path
import sys

from oslo_log import log as logging
from oslo_serialization import jsonutils

from saharaclient.osc.v1 import job_types as jt_v1


class ListJobTypes(jt_v1.ListJobTypes):
    """Lists job types supported by plugins"""

    log = logging.getLogger(__name__ + ".ListJobTypes")


class GetJobTypeConfigs(jt_v1.GetJobTypeConfigs):
    """Get job type configs"""

    log = logging.getLogger(__name__ + ".GetJobTypeConfigs")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        if not parsed_args.file:
            parsed_args.file = parsed_args.job_type

        data = client.job_templates.get_configs(parsed_args.job_type).to_dict()

        if path.exists(parsed_args.file):
            self.log.error('File "%s" already exists. Choose another one with '
                           '--file argument.' % parsed_args.file)
        else:
            with open(parsed_args.file, 'w') as f:
                jsonutils.dump(data, f, indent=4)
            sys.stdout.write(
                '"%(type)s" job configs were saved in "%(file)s"'
                'file' % {'type': parsed_args.job_type,
                          'file': parsed_args.file})
