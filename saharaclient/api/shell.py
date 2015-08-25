# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import datetime
import inspect
import json
import os.path
import sys

from saharaclient.openstack.common.apiclient import exceptions
from saharaclient.openstack.common import cliutils as utils


def _print_list_field(field):
    return lambda obj: ', '.join(getattr(obj, field))


def _filter_call_args(args, func, remap={}):
    """Filter args according to func's parameter list.

    Take three arguments:
     * args - a dictionary
     * func - a function
     * remap - a dictionary
    Remove from dct all the keys which are not among the parameters
    of func. Before filtering, remap the keys in the args dict
    according to remap dict.
    """

    for name, new_name in remap.items():
        if name in args:
            args[new_name] = args[name]
            del args[name]

    valid_args = inspect.getargspec(func).args
    for name in args.keys():
        if name not in valid_args:
            print('WARNING: "%s" is not a valid parameter and will be '
                  'discarded from the request' % name)
            del args[name]


def _print_node_group_field(cluster):
    return ', '.join(map(lambda x: ': '.join(x),
                         [(node_group['name'],
                           str(node_group['count']))
                          for node_group in cluster.node_groups]))


def _show_node_group_template(template):
    template._info['node_processes'] = (
        ', '.join(template._info['node_processes'])
    )
    utils.print_dict(template._info)


def _show_cluster_template(template):
    template._info['node_groups'] = _print_node_group_field(template)
    utils.print_dict(template._info)


def _show_cluster(cluster):
    # TODO(mattf): Make this pretty, e.g format node_groups and info urls
    # Forcing wrap=47 allows for clean display on a terminal of width 80
    utils.print_dict(cluster._info, wrap=47)


def _show_job_binary_data(data):
    columns = ('id', 'name')
    utils.print_list(data, columns)


def _show_data_source(source):
    # TODO(mattf): why are we passing credentials around like this?
    if 'credentials' in source._info:
        del source._info['credentials']
    utils.print_dict(source._info)


def _show_job_binary(binary):
    # TODO(mattf): why are we passing credentials around like this?
    if 'extra' in binary._info:
        del binary._info['extra']
    utils.print_dict(binary._info)


def _show_job_template(template):
    # TODO(mattf): Make "mains" property pretty
    # TODO(mattf): handle/remove "extra" creds
    utils.print_dict(template._info)


def _show_job(job):
    # TODO(mattf): make display of info pretty, until then
    #              extract the important status information
    job._info['status'] = job._info['info']['status']
    del job._info['info']
    utils.print_dict(job._info)


def _get_by_id_or_name(manager, id=None, name=None, **kwargs):
    if not (name or id):
        raise exceptions.CommandError("either NAME or ID is required")
    if id:
        return manager.get(id, **kwargs)
    ls = manager.find(name=name)
    if len(ls) == 0:
        raise exceptions.CommandError("%s '%s' not found" %
                                      (manager.resource_class.resource_name,
                                       name))
    elif len(ls) > 1:
        raise exceptions.CommandError("%s '%s' not unique, try by ID" %
                                      (manager.resource_class.resource_name,
                                       name))
    return manager.get(ls[0].id, **kwargs)


#
# Plugins
# ~~~~~~~
# plugin-list
#
# plugin-show --name <plugin> [--version <version>]
#

def do_plugin_list(cs, args):
    """Print a list of available plugins."""
    plugins = cs.plugins.list()
    columns = ('name', 'versions', 'title')
    utils.print_list(plugins, columns,
                     {'versions': _print_list_field('versions')})


@utils.arg('--name',
           metavar='<plugin>',
           required=True,
           help='Name of the plugin.')
# TODO(mattf) - saharaclient does not support query w/ version
# @utils.arg('--version',
#           metavar='<version>',
#           help='Optional version')
def do_plugin_show(cs, args):
    """Show details of a plugin."""
    plugin = cs.plugins.get(args.name)
    plugin._info['versions'] = ', '.join(plugin._info['versions'])
    utils.print_dict(plugin._info)


#
# Image Registry
# ~~~~~~~~~~~~~~
# image-list [--tag <tag>]*
#
# image-show --name <image>|--id <image_id>
#
# image-register --name <image>|--id <image_id>
#                [--username <name>] [--description <desc>]
#
# image-unregister --name <image>|--id <image_id>
#
# image-add-tag --name <image>|--id <image_id> --tag <tag>+
#
# image-remove-tag --name <image>|--id <image_id> --tag <tag>+
#

# TODO(mattf): [--tag <tag>]*
def do_image_list(cs, args):
    """Print a list of available images."""
    images = cs.images.list()
    columns = ('name', 'id', 'username', 'tags', 'description')
    utils.print_list(images, columns, {'tags': _print_list_field('tags')})


@utils.arg('--name',
           help='Name of the image.')
@utils.arg('--id',
           metavar='<image_id>',
           help='ID of the image.')
def do_image_show(cs, args):
    """Show details of an image."""
    image = _get_by_id_or_name(cs.images, args.id, args.name)
    del image._info['metadata']
    image._info['tags'] = ', '.join(image._info['tags'])
    utils.print_dict(image._info)


# TODO(mattf): Add --name, must lookup in glance index
@utils.arg('--id',
           metavar='<image_id>',
           required=True,
           help='ID of image, run "glance image-list" to see all IDs.')
@utils.arg('--username',
           default='root',
           metavar='<name>',
           help='Username of privileged user in the image.')
@utils.arg('--description',
           default='',
           metavar='<desc>',
           help='Description of the image.')
def do_image_register(cs, args):
    """Register an image from the Image index."""
    # TODO(mattf): image register should not be through update
    cs.images.update_image(args.id, args.username, args.description)
    # TODO(mattf): No indication of result, expect image details


@utils.arg('--name',
           help='Name of the image.')
@utils.arg('--id',
           metavar='<image_id>',
           help='ID of image to unregister.')
def do_image_unregister(cs, args):
    """Unregister an image."""
    cs.images.unregister_image(
        args.id or _get_by_id_or_name(cs.images, name=args.name).id
    )
    # TODO(mattf): No indication of result, expect result to display


@utils.arg('--name',
           help='Name of the image.')
@utils.arg('--id',
           metavar='<image_id>',
           help='ID of image to tag.')
# TODO(mattf): Change --tag to --tag+
@utils.arg('--tag',
           metavar='<tag>',
           required=True,
           help='Tag to add.')
def do_image_add_tag(cs, args):
    """Add a tag to an image."""
    # TODO(mattf): Need proper add_tag API call
    id = args.id or _get_by_id_or_name(cs.images, name=args.name).id
    cs.images.update_tags(id, cs.images.get(id).tags + [args.tag, ])
    # TODO(mattf): No indication of result, expect image details


@utils.arg('--name',
           help='Name of the image.')
@utils.arg('--id',
           metavar='<image_id>',
           help='Image to tag.')
# TODO(mattf): Change --tag to --tag+
@utils.arg('--tag',
           metavar='<tag>',
           required=True,
           help='Tag to remove.')
def do_image_remove_tag(cs, args):
    """Remove a tag from an image."""
    # TODO(mattf): Need proper remove_tag API call
    id = args.id or _get_by_id_or_name(cs.images, name=args.name).id
    cs.images.update_tags(id,
                          filter(lambda x: x != args.tag,
                                 cs.images.get(id).tags))
    # TODO(mattf): No indication of result, expect image details


#
# Clusters
# ~~~~~~~~
# cluster-list
#
# cluster-show --name <cluster>|--id <cluster_id> [--json] [--show-progress]
#
# cluster-create [--json <file>]
#
# cluster-scale --name <cluster>|--id <cluster_id> [--json <file>]
#
# cluster-delete --name <cluster>|--id <cluster_id>
#

def do_cluster_list(cs, args):
    """Print a list of available clusters."""
    clusters = cs.clusters.list()
    for cluster in clusters:
        cluster.node_count = sum(map(lambda g: g['count'],
                                     cluster.node_groups))
    columns = ('name', 'id', 'status', 'node_count')
    utils.print_list(clusters, columns)


@utils.arg('--name',
           help='Name of the cluster.')
@utils.arg('--id',
           metavar='<cluster_id>',
           help='ID of the cluster to show.')
@utils.arg('--show-progress',
           help='Show provision progress events of the cluster.')
@utils.arg('--json',
           action='store_true',
           default=False,
           help='Print JSON representation of the cluster.')
def do_cluster_show(cs, args):
    """Show details of a cluster."""
    cluster = _get_by_id_or_name(cs.clusters, args.id, args.name,
                                 show_progress=args.show_progress)
    if args.json:
        print(json.dumps(cluster._info))
    else:
        _show_cluster(cluster)


@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON representation of cluster.')
@utils.arg('--count',
           default=1,
           type=int,
           help='Number of clusters to create.')
def do_cluster_create(cs, args):
    """Create a cluster."""
    # TODO(mattf): improve template validation, e.g. template w/o name key
    template = json.loads(args.json.read())
    # The neutron_management_network parameter to clusters.create is
    # called net_id. Therefore, we must translate before invoking
    # create w/ **template. It may be desirable to simple change
    # clusters.create in the future.
    remap = {'neutron_management_network': 'net_id'}
    template['count'] = args.count
    _filter_call_args(template, cs.clusters.create, remap)

    _show_cluster(cs.clusters.create(**template))


@utils.arg('--name',
           help='Name of the cluster.')
@utils.arg('--id',
           metavar='<cluster_id>',
           help='ID of the cluster.')
@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON representation of cluster scale.')
def do_cluster_scale(cs, args):
    """Scale a cluster."""
    cluster_id = args.id or _get_by_id_or_name(cs.clusters, name=args.name).id
    scale_template = json.loads(args.json.read())
    _show_cluster(cs.clusters.scale(cluster_id, **scale_template))


@utils.arg('--name',
           help='Name of the cluster.')
@utils.arg('--id',
           metavar='<cluster_id>',
           help='ID of the cluster to delete.')
def do_cluster_delete(cs, args):
    """Delete a cluster."""
    cs.clusters.delete(
        args.id or _get_by_id_or_name(cs.clusters, name=args.name).id
    )
    # TODO(mattf): No indication of result


#
# Node Group Templates
# ~~~~~~~~~~~~~~~~~~~~
# node-group-template-list
#
# node-group-template-show --name <template>|--id <template_id> [--json]
#
# node-group-template-create [--json <file>]
#
# node-group-template-delete --name <template>|--id <template_id>
#
# node-group-template-update --name <template>|--id <template_id> --json <file>
#

def do_node_group_template_list(cs, args):
    """Print a list of available node group templates."""
    templates = cs.node_group_templates.list()
    columns = ('name', 'id', 'plugin_name', 'node_processes', 'description')
    utils.print_list(templates, columns,
                     {'node_processes': _print_list_field('node_processes')})


@utils.arg('--name',
           help='Name of the node group template.')
@utils.arg('--id',
           metavar='<template_id>',
           help='ID of the node group template to show.')
@utils.arg('--json',
           action='store_true',
           default=False,
           help='Print JSON representation of node group template.')
def do_node_group_template_show(cs, args):
    """Show details of a node group template."""
    template = _get_by_id_or_name(cs.node_group_templates, args.id, args.name)
    if args.json:
        print(json.dumps(template._info))
    else:
        _show_node_group_template(template)


@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON representation of node group template.')
def do_node_group_template_create(cs, args):
    """Create a node group template."""
    # TODO(mattf): improve template validation, e.g. template w/o name key
    template = json.loads(args.json.read())
    _filter_call_args(template, cs.node_group_templates.create)

    _show_node_group_template(cs.node_group_templates.create(**template))


@utils.arg('--name',
           help='Name of the node group template.')
@utils.arg('--id',
           metavar='<template_id>',
           help='ID of the node group template to delete.')
def do_node_group_template_delete(cs, args):
    """Delete a node group template."""
    cs.node_group_templates.delete(
        args.id or
        _get_by_id_or_name(cs.node_group_templates, name=args.name).id
    )
    # TODO(mattf): No indication of result


@utils.arg('--name',
           help='Name of the node group template to update.')
@utils.arg('--id',
           metavar='<template_id>',
           help='ID of the node group template to update.')
@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON representation of the node group template update.')
def do_node_group_template_update(cs, args):
    """Update a node group template."""
    template = _get_by_id_or_name(cs.node_group_templates,
                                  name=args.name,
                                  id=args.id)
    update_template = json.loads(args.json.read())
    _filter_call_args(update_template, cs.node_group_templates.update)
    for param in ["plugin_name", "hadoop_version", "name", "flavor_id"]:
        if param not in update_template:
            update_template[param] = getattr(template, param, None)

    result = cs.node_group_templates.update(
        args.id or
        template._get_by_id_or_name(cs.node_group_templates,
                                    name=args.name).id,
        **update_template
    )

    _show_node_group_template(result)


#
# Cluster Templates
# ~~~~~~~~~~~~~~~~~
# cluster-template-list
#
# cluster-template-show --name <template>|--id <template_id> [--json]
#
# cluster-template-create [--json <file>]
#
# cluster-template-delete --name <template>|--id <template_id>
#

def do_cluster_template_list(cs, args):
    """Print a list of available cluster templates."""
    templates = cs.cluster_templates.list()
    columns = ('name', 'id', 'plugin_name', 'node_groups', 'description')
    utils.print_list(templates, columns,
                     {'node_groups': _print_node_group_field})


@utils.arg('--name',
           help='Name of the cluster template.')
@utils.arg('--id',
           metavar='<template_id>',
           help='ID of the cluster template to show.')
@utils.arg('--json',
           action='store_true',
           default=False,
           help='Print JSON representation of cluster template.')
def do_cluster_template_show(cs, args):
    """Show details of a cluster template."""
    template = _get_by_id_or_name(cs.cluster_templates, args.id, args.name)
    if args.json:
        print(json.dumps(template._info))
    else:
        _show_cluster_template(template)


@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON representation of cluster template.')
def do_cluster_template_create(cs, args):
    """Create a cluster template."""
    # TODO(mattf): improve template validation, e.g. template w/o name key
    template = json.loads(args.json.read())
    remap = {'neutron_management_network': 'net_id'}
    _filter_call_args(template, cs.cluster_templates.create, remap)

    _show_cluster_template(cs.cluster_templates.create(**template))


@utils.arg('--name',
           help='Name of the cluster template.')
@utils.arg('--id',
           metavar='<template_id>',
           help='ID of the cluster template to delete.')
def do_cluster_template_delete(cs, args):
    """Delete a cluster template."""
    cs.cluster_templates.delete(
        args.id or _get_by_id_or_name(cs.cluster_templates, name=args.name).id
    )
    # TODO(mattf): No indication of result


@utils.arg('--name',
           help='Name of the cluster template to update.')
@utils.arg('--id',
           metavar='<template_id>',
           help='ID of the cluster template to update.')
@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON representation of cluster template update.')
def do_cluster_template_update(cs, args):
    """Update a cluster template."""
    template = _get_by_id_or_name(cs.cluster_templates,
                                  name=args.name,
                                  id=args.id)
    update_template = json.loads(args.json.read())
    _filter_call_args(update_template, cs.cluster_templates.update)
    for param in ["name", "plugin_name", "hadoop_version"]:
        if param not in update_template:
            update_template[param] = getattr(template, param, None)

    result = cs.cluster_templates.update(
        args.id or
        _get_by_id_or_name(cs.node_group_templates, name=args.name).id,
        **update_template
    )

    _show_cluster_template(result)


#
# Data Sources
# ~~~~~~~~~~~~
# data-source-list
#
# data-source-show --name <name>|--id <id>
#
# data-source-create --name <name> --type <type>
#                    --url <url>
#                    [--user <user> --password <password>]
#                    [--description <desc>]
# NB: user & password if type is swift
#
# data-source-delete --name <name>|--id <id>
#

def do_data_source_list(cs, args):
    """Print a list of available data sources."""
    sources = cs.data_sources.list()
    columns = ('name', 'id', 'type', 'description')
    utils.print_list(sources, columns)


@utils.arg('--name',
           help='Name of the data source.')
@utils.arg('--id',
           help='ID of the data source.')
def do_data_source_show(cs, args):
    """Show details of a data source."""
    _show_data_source(_get_by_id_or_name(cs.data_sources, args.id, args.name))


@utils.arg('--name',
           required=True,
           help='Name of the data source.')
@utils.arg('--type',
           required=True,
           help='Type of the data source.')
@utils.arg('--url',
           required=True,
           help='URL for the data source.')
@utils.arg('--description',
           default='',
           help='Description of the data source.')
@utils.arg('--user',
           default=None,
           help='Username for accessing the data source URL.')
@utils.arg('--password',
           default=None,
           help='Password for accessing the data source URL.')
def do_data_source_create(cs, args):
    """Create a data source that provides job input or receives job output."""
    _show_data_source(cs.data_sources.create(args.name, args.description,
                                             args.type, args.url,
                                             args.user, args.password))


@utils.arg('--name',
           help='Name of the data source.')
@utils.arg('--id',
           help='ID of data source to delete.')
def do_data_source_delete(cs, args):
    """Delete a data source."""
    cs.data_sources.delete(
        args.id or _get_by_id_or_name(cs.data_sources, name=args.name).id
    )
    # TODO(mattf): No indication of result


@utils.arg('--name',
           help="Name of the data source to update.")
@utils.arg('--id',
           help="ID of the data source to update.")
@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON containing the data source fields to update.')
def do_data_source_update(cs, args):
    """Update a data source."""
    update_data = json.loads(args.json.read())
    result = cs.data_sources.update(
        args.id or _get_by_id_or_name(cs.data_sources, name=args.name).id,
        update_data
    )
    _show_data_source(result)


#
# Job Binary Internals
# ~~~~~~~~~~~~~~~~~~~~
# job-binary-data-list
#
# job-binary-data-create [--file <file>] [--name <name>]
#
# job-binary-data-delete --id <id>
#

def do_job_binary_data_list(cs, args):
    """Print a list of internally stored job binary data."""
    _show_job_binary_data(cs.job_binary_internals.list())


@utils.arg('--file',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='Data to store.')
@utils.arg('--name',
           help="Name of the job binary internal.")
def do_job_binary_data_create(cs, args):
    """Store data in the internal DB.

    Use 'swift upload' instead of this command.
    Use this command only if Swift is not available.
    """
    if args.name:
        name = args.name
    elif args.file is not sys.stdin:
        name = os.path.basename(args.file.name)
    else:
        name = datetime.datetime.now().strftime('d%Y%m%d%H%M%S')
    # Should be %F-%T except for type validation errors
    _show_job_binary_data((cs.job_binary_internals.create(
        name,
        args.file.read()),)
    )


@utils.arg('--id',
           required=True,
           help='ID of internally stored job binary data.')
def do_job_binary_data_delete(cs, args):
    """Delete an internally stored job binary data."""
    cs.job_binary_internals.delete(args.id)
    # TODO(mattf): No indication of result
    # TODO(mattf): Appears no DB constraints for removing data used by job


#
# Job Binaries
# ~~~~~~~~~~~~
# job-binary-list
#
# job-binary-show --name <name>|--id <id>
#
# job-binary-create --name <name> --url <url>
#                   [--user <user> --password <password>]
#                   [--description <desc>]
#
# job-binary-delete --name <name>|--id <id>
#

def do_job_binary_list(cs, args):
    """Print a list of job binaries."""
    binaries = cs.job_binaries.list()
    columns = ('id', 'name', 'description')
    utils.print_list(binaries, columns)


@utils.arg('--name',
           help='Name of the job binary.')
@utils.arg('--id',
           help='ID of the job binary.')
def do_job_binary_show(cs, args):
    """Show details of a job binary."""
    _show_job_binary(_get_by_id_or_name(cs.job_binaries, args.id, args.name))


@utils.arg('--name',
           required=True,
           help='Name of the job binary.')
@utils.arg('--url',
           required=True,
           help='URL for the job binary.')
@utils.arg('--description',
           default='',
           help='Description of the job binary.')
@utils.arg('--user',
           default=None,
           help='Username for accessing the job binary URL.')
@utils.arg('--password',
           default=None,
           help='Password for accessing the job binary URL.')
def do_job_binary_create(cs, args):
    """Record a job binary."""
    # TODO(mattf): make credentials consistent w/ data source
    extra = {}
    if args.user:
        extra['user'] = args.user
    if args.password:
        extra['password'] = args.password
    _show_job_binary(cs.job_binaries.create(args.name, args.url,
                                            args.description, extra))


@utils.arg('--name',
           help='Name of the job binary.')
@utils.arg('--id',
           help='ID of the job binary to delete.')
def do_job_binary_delete(cs, args):
    """Delete a job binary."""
    cs.job_binaries.delete(
        args.id or _get_by_id_or_name(cs.job_binaries, name=args.name).id
    )
    # TODO(mattf): No indication of result


@utils.arg('--name',
           help='Name of the job binary to update.')
@utils.arg('--id',
           metavar='<job_binary_id>',
           help='ID of the job binary to update.')
@utils.arg('--json',
           default=sys.stdin,
           type=argparse.FileType('r'),
           help='JSON representation of job binary update.')
def do_job_binary_update(cs, args):
    """Update a job binary."""
    update_data = json.loads(args.json.read())
    result = cs.job_binaries.update(
        args.id or
        _get_by_id_or_name(cs.job_binaries, name=args.name).id,
        update_data
    )

    _show_job_binary(result)


#
# Jobs
# ~~~~
# job-template-list
#
# job-template-show --name <name>|--id <id>
#
# job-template-create --name <name>
#                     --type <Pig|Hive|MapReduce|Java|...>
#                     [--mains <array of string>]
#                     [--libs <array of string>]
#                     [--description <desc>]
#
# job-template-delete --name <name>|--id <id>
#

def do_job_template_list(cs, args):
    """Print a list of job templates."""
    templates = cs.jobs.list()
    columns = ('id', 'name', 'description')
    utils.print_list(templates, columns)


@utils.arg('--name',
           help='Name of the job template.')
@utils.arg('--id',
           help='ID of the job template.')
def do_job_template_show(cs, args):
    """Show details of a job template."""
    _show_job_template(_get_by_id_or_name(cs.jobs, args.id, args.name))


@utils.arg('--name',
           help='Name of the job template.')
@utils.arg('--type',
           help='Type of the job template.')
@utils.arg('--main',
           action='append',
           default=[],
           help='ID for job\'s main job-binary.')
@utils.arg('--lib',
           action='append',
           default=[],
           help='ID of job\'s lib job-binary, repeatable.')
@utils.arg('--description',
           default='',
           help='Description of the job template.')
@utils.arg('--json',
           default=None,
           type=argparse.FileType('r'),
           help='JSON representation of job template.')
def do_job_template_create(cs, args):
    """Create a job template."""
    template = json.loads(args.json.read()) if args.json else {}
    _filter_call_args(template, cs.jobs.create)
    template = {
        "name": args.name or template.get("name") or None,
        "type": args.type or template.get("type") or None,
        "mains": args.main or template.get("mains") or [],
        "libs": args.lib or template.get("libs") or [],
        "description": args.description or template.get("description") or '',
        "interface": template.get("interface") or []
    }
    if not template["name"]:
        raise Exception("name is required")
    if not template["type"]:
        raise Exception("type is required")

    _show_job_template(cs.jobs.create(**template))


@utils.arg('--name',
           help='Name of the job template.')
@utils.arg('--id',
           help='ID of the job template.')
def do_job_template_delete(cs, args):
    """Delete a job template."""
    cs.jobs.delete(
        args.id or _get_by_id_or_name(cs.jobs, name=args.name).id
    )
    # TODO(mattf): No indication of result


#
# Job Executions
# ~~~~~~~~~~~~~~
# job-list
#
# job-show --id <id>
#
# job-create --job-template <id> --cluster <id>
#            [--input-data <id>] [--output-data <id>]
#            [--param <name=value>]
#            [--arg <arg>]
#            [--config <name=value>]
#
# job-delete --id <id>
#

def do_job_list(cs, args):
    """Print a list of jobs."""
    jobs = cs.job_executions.list()
    for job in jobs:
        # why is status in info.status?
        job.status = job.info['status']
    # TODO(mattf): why can cluster_id be None?
    columns = ('id', 'cluster_id', 'start_time', 'status')
    utils.print_list(jobs, columns, sortby_index=2)


@utils.arg('--id',
           required=True,
           help='ID of the job.')
def do_job_show(cs, args):
    """Show details of a job."""
    _show_job(cs.job_executions.get(args.id))


@utils.arg('--job-template',
           required=True,
           help='ID of the job template to run.')
@utils.arg('--cluster',
           required=False,
           help='ID of the cluster to run the job in.')
@utils.arg('--input-data',
           default=None,
           help='ID of the input data source.')
@utils.arg('--output-data',
           default=None,
           help='ID of the output data source.')
@utils.arg('--param',
           metavar='name=value',
           action='append',
           default=[],
           help='Parameters to add to the job, repeatable.')
@utils.arg('--arg',
           action='append',
           default=[],
           help='Arguments to add to the job, repeatable.')
@utils.arg('--config',
           metavar='name=value',
           action='append',
           default=[],
           help='Config parameters to add to the job, repeatable.')
@utils.arg('--json',
           default=None,
           type=argparse.FileType('r'),
           help='JSON representation of the job.')
def do_job_create(cs, args):
    """Create a job."""
    job = json.loads(args.json.read()) if args.json else {}
    remap = {"job_configs": "configs"}
    _filter_call_args(job, cs.job_executions.create, remap)
    _convert = lambda ls: dict(map(lambda i: i.split('=', 1), ls))
    job = {
        "cluster_id": args.cluster or job.get("cluster_id") or None,
        "input_id": args.input_data or job.get("input_id") or None,
        "output_id": args.output_data or job.get("output_id") or None,
        "interface": job.get("interface") or [],
        "configs": job.get("configs") or {}
    }
    if any((args.config, args.param, args.arg)):
        job["configs"] = {"configs": _convert(args.config),
                          "args": args.arg,
                          "params": _convert(args.param)}
    if not job["cluster_id"]:
        raise Exception("cluster is required")
    _show_job(cs.job_executions.create(args.job_template, **job))


@utils.arg('--id',
           required=True,
           help='ID of a job.')
def do_job_delete(cs, args):
    """Delete a job."""
    cs.job_executions.delete(args.id)
    # TODO(mattf): No indication of result


#
# Job Types
# ~~~~~~~~~
# job-type-list [--type] [--plugin [--plugin-version]]
#

def _print_plugin_field(job_type):

    def plugin_version_string(plugin):
        versions = ", ".join(plugin["versions"].keys())
        if versions:
            versions = "(" + versions + ")"
        return plugin["name"] + versions

    return ", ".join(map(lambda x: plugin_version_string(x), job_type.plugins))


@utils.arg('--type',
           metavar='<job_type>',
           default=None,
           help='Report only on this job type.')
@utils.arg('--plugin',
           metavar='<plugin>',
           default=None,
           help='Report only job types supported by this plugin.')
@utils.arg('--plugin-version',
           metavar='<plugin_version>',
           default=None,
           help='Report only on job types supported by this version '
           'of a specified plugin. Only valid with --plugin.')
def do_job_type_list(cs, args):
    """Show supported job types."""
    search_opts = {}
    if args.type:
        search_opts["type"] = args.type
    if args.plugin:
        search_opts["plugin"] = args.plugin
        if args.plugin_version:
            search_opts["version"] = args.plugin_version
    elif args.plugin_version:
        raise exceptions.CommandError(
            'The --plugin-version option is only valid when '
            '--plugin is specified')

    job_types = cs.job_types.list(search_opts)
    columns = ('name', 'plugin(versions)')
    utils.print_list(job_types, columns,
                     {'plugin(versions)': _print_plugin_field})
