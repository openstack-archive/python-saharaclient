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


import inspect
import os
import sys

from docutils import nodes
from . import ext


def _get_command(classes):
    """Associates each command class with command depending on setup.cfg
    """
    commands = {}
    setup_file = os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')),
        'setup.cfg')
    for line in open(setup_file, 'r'):
        for cl in classes:
            if cl in line:
                commands[cl] = line.split(' = ')[0].strip().replace('_', ' ')

    return commands


class ArgParseDirectiveOSC(ext.ArgParseDirective):
    """Sphinx extension that automatically documents commands and options
    of the module that contains OpenstackClient/cliff command objects

    Usage example:

    .. cli::
       :module: saharaclient.osc.v1.clusters

    """
    def run(self):
        module_name = self.options['module']

        mod = __import__(module_name, globals(), locals())

        classes = inspect.getmembers(sys.modules[module_name], inspect.isclass)
        classes_names = [cl[0] for cl in classes]
        commands = _get_command(classes_names)

        items = []

        for cl in classes:
            parser = cl[1](None, None).get_parser(None)
            parser.prog = commands[cl[0]]
            items.append(nodes.subtitle(text=commands[cl[0]]))
            result = ext.parse_parser(
                parser, skip_default_values='nodefault' in self.options)
            result = ext.parser_navigate(result, '')
            nested_content = ext.nodes.paragraph()
            self.state.nested_parse(
                self.content, self.content_offset, nested_content)
            nested_content = nested_content.children

            for item in nested_content:
                if not isinstance(item, ext.nodes.definition_list):
                    items.append(item)
            if 'description' in result:
                items.append(self._nested_parse_paragraph(result['description']))
            items.append(ext.nodes.literal_block(text=result['usage']))
            items.append(ext.print_command_args_and_opts(
                ext.print_arg_list(result, nested_content),
                ext.print_opt_list(result, nested_content),
                ext.print_subcommand_list(result, nested_content)
            ))
            if 'epilog' in result:
                items.append(self._nested_parse_paragraph(result['epilog']))
        return items


def setup(app):
    app.add_directive('cli', ArgParseDirectiveOSC)
