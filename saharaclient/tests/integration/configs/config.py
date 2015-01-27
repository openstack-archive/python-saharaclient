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

from oslo_config import cfg


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
               help='The BYPASS_URL value to pass to the cli'),
    cfg.StrOpt('SWIFT_AUTH_VERSION',
               default=2,
               help='OpenStack auth version for Swift.'),
    cfg.IntOpt('CLUSTER_CREATION_TIMEOUT',
               default=10,
               help='Cluster creation timeout (in minutes); '
               'minimal value is 1.'),
    cfg.StrOpt('USER_KEYPAIR_ID',
               help='A keypair id to use during cluster launch. '
               'If the id is left blank, an id will be generated. '
               'If the id names an existing keypair, that keypair will '
               'be used. If the named keypair does not exist, it will be '
               'created and deleted after the test.'),
    cfg.IntOpt('DELAY_AFTER_ACTIVE',
               default=2,
               help='Length of time (in minutes) to '
               'wait after cluster is active before running jobs.'),
    cfg.StrOpt('FLOATING_IP_POOL',
               help='Pool name for floating IPs. If Sahara uses Nova '
                    'management network and auto assignment of IPs was '
                    'enabled then you should leave default value of this '
                    'parameter. If auto assignment was not enabled, then you '
                    'should specify value (floating IP pool name) of this '
                    'parameter. If Sahara uses Neutron management network, '
                    'then you should always specify value (floating IP pool '
                    'name) of this parameter.'),
    cfg.BoolOpt('NEUTRON_ENABLED',
                default=False,
                help='If Sahara uses Nova management network, then you '
                     'should leave default value of this flag. If Sahara '
                     'uses Neutron management network, then you should set '
                     'this flag to True and specify values of the following '
                     'parameters: FLOATING_IP_POOL and '
                     'INTERNAL_NEUTRON_NETWORK.'),
    cfg.StrOpt('INTERNAL_NEUTRON_NETWORK',
               default='private',
               help='Name for internal Neutron network.'),
    cfg.IntOpt('JOB_LAUNCH_TIMEOUT',
               default=10,
               help='Job launch timeout (in minutes); '
               'minimal value is 1.'),
    cfg.BoolOpt('INTERNAL_JOB_BINARIES',
                default=True,
                help='Store job binary data in the sahara '
                'internal database.  If this option is set to '
                'False, job binary data will be stored in swift.'),
    cfg.StrOpt('CLUSTER_NAME',
               default='test',
               help='Name for cluster.')
]


def general_cluster_config_opts(plugin_text, plugin_name, hadoop_ver,
                                skip_all=False):
    return [
        cfg.StrOpt('EXISTING_CLUSTER_ID',
                   help='The id of an existing active cluster '
                   'to use for the test instead of building one. '
                   'Cluster teardown will be skipped. This has priority '
                   'over EXISTING_CLUSTER_NAME'),
        cfg.StrOpt('EXISTING_CLUSTER_NAME',
                   help='The name of an existing active cluster '
                   'to use for the test instead of building one. '
                   'Cluster teardown will be skipped. This is superseded '
                   'by EXISTING_CLUSTER_ID'),
        cfg.StrOpt('IMAGE_ID',
                   help='ID for image which is used for cluster creation. '
                   'You can also specify image name or tag of image instead '
                   'of image ID. If you do not specify image related '
                   'parameters then the image for cluster creation will be '
                   'chosen by tag "sahara_i_tests".'),
        cfg.StrOpt('IMAGE_NAME',
                   help='Name for image which is used for cluster creation. '
                   'You can also specify image ID or tag of image instead of '
                   'image name. If you do not specify image related '
                   'parameters then the image for cluster creation will be '
                   'chosen by tag "sahara_i_tests".'),
        cfg.StrOpt('IMAGE_TAG',
                   help='Tag for image which is used for cluster creation. '
                   'You can also specify image ID or image name instead of '
                   'the image tag. If you do not specify image related '
                   'parameters, then the image for cluster creation will be '
                   'chosen by the tag "sahara_i_tests".'),
        cfg.StrOpt('SSH_USERNAME',
                   help='Username used to log into a cluster node via SSH.'),
        cfg.StrOpt('HADOOP_VERSION',
                   default='%s' % hadoop_ver,
                   help='Version of Hadoop'),
        cfg.StrOpt('PLUGIN_NAME',
                   default='%s' % plugin_name,
                   help='Name of plugin'),
        cfg.BoolOpt('SKIP_ALL_TESTS_FOR_PLUGIN',
                    default=skip_all,
                    help='If this flag is True, then all tests for the %s '
                    'plugin will be skipped.' % plugin_text),
        cfg.BoolOpt('SKIP_CLUSTER_TEARDOWN',
                    default=False,
                    help='Skip tearing down the cluster. If an existing '
                    'cluster is used it will never be torn down by the test.'),
        cfg.BoolOpt('SKIP_JAVA_EDP_TEST', default=False),
        cfg.BoolOpt('SKIP_MAPREDUCE_EDP_TEST', default=False),
        cfg.BoolOpt('SKIP_MAPREDUCE_STREAMING_EDP_TEST', default=False),
        cfg.BoolOpt('SKIP_PIG_EDP_TEST', default=False)
    ]


VANILLA_CONFIG_GROUP = cfg.OptGroup(name='VANILLA')
VANILLA_CONFIG_OPTS = general_cluster_config_opts("Vanilla",
                                                  "vanilla", "1.2.1")

VANILLA2_CONFIG_GROUP = cfg.OptGroup(name='VANILLA2')
VANILLA2_CONFIG_OPTS = general_cluster_config_opts("Vanilla2",
                                                   "vanilla", "2.3.0",
                                                   skip_all=True)

HDP_CONFIG_GROUP = cfg.OptGroup(name='HDP')
HDP_CONFIG_OPTS = general_cluster_config_opts("HDP",
                                              "hdp", "1.3.2",
                                              skip_all=True)


def register_config(config, config_group, config_opts):
    config.register_group(config_group)
    config.register_opts(config_opts, config_group)


@singleton
class ITConfig(object):
    def __init__(self):
        config = 'itest.conf'
        config_files = []
        config_path = '%s/saharaclient/tests/integration/configs/%s'
        if not os.path.exists(config_path % (os.getcwd(), config)):
            message = ('\n**************************************************'
                       '\nINFO: Configuration file "%s" not found  *\n'
                       '**************************************************'
                       % config)
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
