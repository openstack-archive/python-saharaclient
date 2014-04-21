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

from __future__ import print_function

import os
import sys

from oslo.config import cfg


def singleton(cls):
    instances = {}

    def get_instance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return get_instance

COMMON_CONFIG_GROUP = cfg.OptGroup(name='COMMON')
COMMON_CONFIG_OPTS = [
    cfg.StrOpt('OS_USERNAME',
               default='admin',
               help='Username for OpenStack.'),
    cfg.StrOpt('OS_PASSWORD',
               default='admin',
               help='Password for OpenStack.'),
    cfg.StrOpt('OS_TENANT_NAME',
               default='admin',
               help='Tenant name for OpenStack.'),
    cfg.StrOpt('OS_AUTH_URL',
               default='http://127.0.0.1:5000/v2.0',
               help='URL for OpenStack.'),
    cfg.StrOpt('OS_PROJECT_NAME',
               default='admin',
               help='Project name for OpenStack.'),
    cfg.StrOpt('BYPASS_URL',
               default='',
               help='The BYPASS_URL value to pass to the cli'),
    cfg.StrOpt('SWIFT_AUTH_VERSION',
               default=2,
               help='OpenStack auth version for Swift.')
]

VANILLA_CONFIG_GROUP = cfg.OptGroup(name='VANILLA')
VANILLA_CONFIG_OPTS = [
    cfg.BoolOpt('SKIP_ALL_TESTS_FOR_PLUGIN',
                default=False,
                help='If this flag is True, then all tests for Vanilla plugin '
                     'will be skipped.')
]

VANILLA2_CONFIG_GROUP = cfg.OptGroup(name='VANILLA2')
VANILLA2_CONFIG_OPTS = [
    cfg.BoolOpt('SKIP_ALL_TESTS_FOR_PLUGIN',
                default=True,
                help='If this flag is True, then all tests for Vanilla2 plugin'
                     ' will be skipped.')
]

HDP_CONFIG_GROUP = cfg.OptGroup(name='HDP')
HDP_CONFIG_OPTS = [
    cfg.BoolOpt('SKIP_ALL_TESTS_FOR_PLUGIN',
                default=True,
                help='If this flag is True, then all tests for HDP plugin '
                     'will be skipped.')
]


def register_config(config, config_group, config_opts):
    config.register_group(config_group)
    config.register_opts(config_opts, config_group)


@singleton
class ITConfig:
    def __init__(self):
        config = 'itest.conf'
        config_files = []
        config_path = '%s/saharaclient/tests/integration/configs/%s'
        if not os.path.exists(config_path % (os.getcwd(), config)):
            message = '\n**************************************************' \
                      '\nINFO: Configuration file "%s" not found  *\n' \
                      '**************************************************' \
                      % config
            print(message, file=sys.stderr)
        else:
            config = os.path.join(
                config_path % (os.getcwd(), config)
            )
            config_files.append(config)

        register_config(cfg.CONF, COMMON_CONFIG_GROUP, COMMON_CONFIG_OPTS)
        register_config(cfg.CONF, VANILLA_CONFIG_GROUP, VANILLA_CONFIG_OPTS)
        register_config(cfg.CONF, VANILLA2_CONFIG_GROUP, VANILLA2_CONFIG_OPTS)
        register_config(cfg.CONF, HDP_CONFIG_GROUP, HDP_CONFIG_OPTS)

        cfg.CONF(
            [], project='Sahara_client_integration_tests',
            default_config_files=config_files
        )
        self.common_config = cfg.CONF.COMMON
        self.vanilla_config = cfg.CONF.VANILLA
        self.hdp_config = cfg.CONF.HDP
        self.vanilla2_config = cfg.CONF.VANILLA2
