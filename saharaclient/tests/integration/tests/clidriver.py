# Copyright (c) 2014 Red Hat Inc.
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

import logging
import shlex
import subprocess

from saharaclient.tests.integration.configs import config as cfg

cfg = cfg.ITConfig()

LOG = logging.getLogger(__name__)


# This is modeled after the client interface in tempest cli tests.2
class CommandBase(object):
    def sahara(self, action, flags='', params='', fail_ok=False):
        return self.cmd_with_bypass('sahara', action, flags, params, fail_ok)

    def cmd_with_bypass(self, cmd, action, flags='', params='', fail_ok=False):
        if cfg.common_config['BYPASS_URL']:
            bypass = '--bypass-url %s' % cfg.common_config['BYPASS_URL']
            flags = bypass + ' ' + flags
        return self.cmd_with_auth(cmd, action, flags, params, fail_ok)

    def cmd_with_auth(self, cmd, action, flags='', params='', fail_ok=False):
        """Executes given command with auth attributes appended."""
        creds = ('--os-username %s --os-tenant-name %s --os-password %s '
                 '--os-auth-url %s ' %
                 (cfg.common_config['OS_USERNAME'],
                  cfg.common_config['OS_TENANT_NAME'],
                  cfg.common_config['OS_PASSWORD'],
                  cfg.common_config['OS_AUTH_URL']))
        flags = creds + ' ' + flags
        return self.cmd(cmd, action, flags, params, fail_ok)

    def cmd(self, cmd, action, flags='', params='', fail_ok=False,
            merge_stderr=False):
        """Executes specified command for the given action."""
        cmd = ' '.join([cmd, flags, action, params])
        LOG.info("running: '%s'", cmd)
        cmd_str = cmd
        cmd = shlex.split(cmd)
        result = ''
        result_err = ''
        try:
            stdout = subprocess.PIPE
            stderr = subprocess.STDOUT if merge_stderr else subprocess.PIPE
            proc = subprocess.Popen(
                cmd, stdout=stdout, stderr=stderr)
            result, result_err = proc.communicate()
            if not fail_ok and proc.returncode != 0:
                raise CommandFailed(proc.returncode,
                                    cmd,
                                    result)
        finally:
            LOG.debug('output of %s:\n%s', cmd_str, result)
            if not merge_stderr and result_err:
                LOG.debug('error output of %s:\n%s', cmd_str, result_err)
        return result


class CommandFailed(subprocess.CalledProcessError):
    # adds output attribute for python2.6
    def __init__(self, returncode, cmd, output):
        super(CommandFailed, self).__init__(returncode, cmd)
        self.output = output


class CLICommands(CommandBase):
    def register_image(self, image_id, username='', description=''):
        params = '--id %s' % image_id
        if username:
            params += ' --username %s' % username
        if description:
            params += ' --description %s' % description
        return self.sahara('image-register', params=params)

    def unregister_image(self, id):
        params = '--id %s' % id
        return self.sahara('image-unregister', params=params)

    def tag_image(self, id, tag):
        params = '--id %s --tag %s' % (id, tag)
        return self.sahara('image-add-tag', params=params)

    def node_group_template_create(self, filename):
        params = '--json %s' % filename
        return self.sahara('node-group-template-create', params=params)

    def node_group_template_delete(self, id):
        params = '--id %s' % id
        return self.sahara('node-group-template-delete', params=params)

    def cluster_template_create(self, filename):
        params = '--json %s' % filename
        return self.sahara('cluster-template-create', params=params)

    def cluster_template_delete(self, id):
        params = '--id %s' % id
        return self.sahara('cluster-template-delete', params=params)

    def cluster_create(self, filename):
        params = '--json %s' % filename
        return self.sahara('cluster-create', params=params)

    def cluster_delete(self, id):
        params = '--id %s' % id
        return self.sahara('cluster-delete', params=params)

    def job_binary_create(self, name, url, desc='', username='', password=''):
        params = '--name %s --url %s' % (name, url)
        if desc:
            params += ' --description %s' % desc
        if username:
            params += ' --user %s' % username
        if password:
            params += ' --password %s' % password
        return self.sahara('job-binary-create', params=params)

    def job_binary_delete(self, id):
        params = '--id %s' % id
        return self.sahara('job-binary-delete', params=params)

    def job_binary_data_create(self, fname):
        params = '--file %s' % fname
        return self.sahara('job-binary-data-create', params=params)

    def job_binary_data_delete(self, id):
        params = '--id %s' % id
        return self.sahara('job-binary-data-delete', params=params)

    def job_template_create(self, filename):
        params = '--json %s' % (filename)
        return self.sahara('job-template-create', params=params)

    def job_template_delete(self, id):
        params = '--id %s' % id
        return self.sahara('job-template-delete', params=params)

    def job_create(self, job_template_id, filename):
        params = '--job-template %s --json %s' % (job_template_id, filename)
        return self.sahara('job-create', params=params)

    def job_delete(self, id):
        params = '--id %s' % id
        return self.sahara('job-delete', params=params)

    def data_source_create(self, name, datatype, url,
                           desc='', username='', password=''):
        params = '--name %s --type %s --url %s' % (name, datatype, url)
        if desc:
            params += ' --description %s' % desc
        if username:
            params += ' --user %s' % username
        if password:
            params += ' --password %s' % password
        return self.sahara('data-source-create', params=params)

    def data_source_delete(self, id):
        params = '--id %s' % id
        return self.sahara('data-source-delete', params=params)
