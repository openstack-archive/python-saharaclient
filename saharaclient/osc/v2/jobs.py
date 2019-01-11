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

import sys

from osc_lib import utils as osc_utils
from oslo_log import log as logging

from saharaclient.osc import utils
from saharaclient.osc.v1 import jobs as jobs_v1


def _format_job_output(app, data):
    data['status'] = data['info']['status']
    del data['info']


class ExecuteJob(jobs_v1.ExecuteJob):
    """Executes job"""

    log = logging.getLogger(__name__ + ".ExecuteJob")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_job_output(self.app, data)
        data = utils.prepare_data(data, jobs_v1.JOB_FIELDS)

        return self.dict2columns(data)


class ListJobs(jobs_v1.ListJobs):
    """Lists jobs"""

    log = logging.getLogger(__name__ + ".ListJobs")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = client.jobs.list()

        for job in data:
            job.status = job.info['status']

        if parsed_args.status:
            data = [job for job in data
                    if job.info['status'] == parsed_args.status.replace(
                        '-', '').upper()]

        if parsed_args.long:
            columns = ('id', 'cluster id', 'job template id', 'status',
                       'start time', 'end time')
            column_headers = utils.prepare_column_headers(columns)

        else:
            columns = ('id', 'cluster id', 'job template id', 'status')
            column_headers = utils.prepare_column_headers(columns)

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns
            ) for s in data)
        )


class ShowJob(jobs_v1.ShowJob):
    """Display job details"""

    log = logging.getLogger(__name__ + ".ShowJob")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = client.jobs.get(parsed_args.job).to_dict()

        _format_job_output(self.app, data)
        data = utils.prepare_data(data, jobs_v1.JOB_FIELDS)

        return self.dict2columns(data)


class DeleteJob(jobs_v1.DeleteJob):
    """Deletes job"""

    log = logging.getLogger(__name__ + ".DeleteJob")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        for job_id in parsed_args.job:
            client.jobs.delete(job_id)
            sys.stdout.write(
                'Job "{job}" deletion has been started.\n'.format(job=job_id))

        if parsed_args.wait:
            for job_id in parsed_args.job:
                wait_for_delete = utils.wait_for_delete(client.jobs, job_id)

                if not wait_for_delete:
                    self.log.error(
                        'Error occurred during job deleting: %s' %
                        job_id)
                else:
                    sys.stdout.write(
                        'Job "{job}" has been removed successfully.\n'.format(
                            job=job_id))


class UpdateJob(jobs_v1.UpdateJob):
    """Updates job"""

    log = logging.getLogger(__name__ + ".UpdateJob")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = self._take_action(client, parsed_args)

        _format_job_output(self.app, data)
        data = utils.prepare_data(data, jobs_v1.JOB_FIELDS)

        return self.dict2columns(data)
