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

from osc_lib.command import command
from osc_lib import utils as osc_utils
from oslo_log import log as logging

from saharaclient.osc import utils

IMAGE_FIELDS = ['name', 'id', 'username', 'tags', 'status', 'description']


class ListImages(command.Lister):
    """Lists registered images"""

    log = logging.getLogger(__name__ + ".ListImages")

    def get_parser(self, prog_name):
        parser = super(ListImages, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        parser.add_argument(
            '--name',
            metavar="<name-regex>",
            help="Regular expression to match image name"
        )
        parser.add_argument(
            '--tags',
            metavar="<tag>",
            nargs="+",
            help="List images with specific tag(s)"
        )
        parser.add_argument(
            '--username',
            metavar="<username>",
            help="List images with specific username"
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        search_opts = {'tags': parsed_args.tags} if parsed_args.tags else {}

        data = client.images.list(search_opts=search_opts)

        if parsed_args.name:
            data = utils.get_by_name_substring(data, parsed_args.name)

        if parsed_args.username:
            data = [i for i in data if parsed_args.username in i.username]

        if parsed_args.long:
            columns = IMAGE_FIELDS
            column_headers = [c.capitalize() for c in columns]

        else:
            columns = ('name', 'id', 'username', 'tags')
            column_headers = [c.capitalize() for c in columns]

        return (
            column_headers,
            (osc_utils.get_item_properties(
                s,
                columns,
                formatters={
                    'tags': osc_utils.format_list
                },
            ) for s in data)
        )


class ShowImage(command.ShowOne):
    """Display image details"""

    log = logging.getLogger(__name__ + ".ShowImage")

    def get_parser(self, prog_name):
        parser = super(ShowImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or id of the image to display",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        data = utils.get_resource(
            client.images, parsed_args.image).to_dict()
        data['tags'] = osc_utils.format_list(data['tags'])

        data = utils.prepare_data(data, IMAGE_FIELDS)

        return self.dict2columns(data)


class RegisterImage(command.ShowOne):
    """Register an image"""

    log = logging.getLogger(__name__ + ".RegisterImage")

    def get_parser(self, prog_name):
        parser = super(RegisterImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or ID of the image to register",
        )
        parser.add_argument(
            "--username",
            metavar="<username>",
            help="Username of privileged user in the image [REQUIRED]",
            required=True
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Description of the image. If not provided, description of "
                 "the image will be reset to empty",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        image_client = self.app.client_manager.image

        image_id = osc_utils.find_resource(
            image_client.images, parsed_args.image).id

        data = client.images.update_image(
            image_id, user_name=parsed_args.username,
            desc=parsed_args.description).image

        data['tags'] = osc_utils.format_list(data['tags'])

        data = utils.prepare_data(data, IMAGE_FIELDS)

        return self.dict2columns(data)


class UnregisterImage(command.Command):
    """Unregister image(s)"""

    log = logging.getLogger(__name__ + ".RegisterImage")

    def get_parser(self, prog_name):
        parser = super(UnregisterImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            nargs="+",
            help="Name(s) or id(s) of the image(s) to unregister",
        )

        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing
        for image in parsed_args.image:
            image_id = utils.get_resource_id(client.images, image)
            client.images.unregister_image(image_id)
            sys.stdout.write(
                'Image "{image}" has been unregistered '
                'successfully.\n'.format(image=image))


class SetImageTags(command.ShowOne):
    """Set image tags (Replace current image tags with provided ones)"""

    log = logging.getLogger(__name__ + ".AddImageTags")

    def get_parser(self, prog_name):
        parser = super(SetImageTags, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or id of the image",
        )
        parser.add_argument(
            '--tags',
            metavar="<tag>",
            nargs="+",
            required=True,
            help="Tag(s) to set [REQUIRED]"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        image_id = utils.get_resource_id(client.images, parsed_args.image)
        data = client.images.update_tags(image_id, parsed_args.tags).to_dict()

        data['tags'] = osc_utils.format_list(data['tags'])

        data = utils.prepare_data(data, IMAGE_FIELDS)

        return self.dict2columns(data)


class AddImageTags(command.ShowOne):
    """Add image tags"""

    log = logging.getLogger(__name__ + ".AddImageTags")

    def get_parser(self, prog_name):
        parser = super(AddImageTags, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or id of the image",
        )
        parser.add_argument(
            '--tags',
            metavar="<tag>",
            nargs="+",
            required=True,
            help="Tag(s) to add [REQUIRED]"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        image = utils.get_resource(client.images, parsed_args.image)
        parsed_args.tags.extend(image.tags)
        data = client.images.update_tags(
            image.id, list(set(parsed_args.tags))).to_dict()

        data['tags'] = osc_utils.format_list(data['tags'])

        data = utils.prepare_data(data, IMAGE_FIELDS)

        return self.dict2columns(data)


class RemoveImageTags(command.ShowOne):
    """Remove image tags"""

    log = logging.getLogger(__name__ + ".RemoveImageTags")

    def get_parser(self, prog_name):
        parser = super(RemoveImageTags, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or id of the image",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--tags',
            metavar="<tag>",
            nargs="+",
            help="Tag(s) to remove"
        ),
        group.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='Remove all tags from image',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        client = self.app.client_manager.data_processing

        image = utils.get_resource(client.images, parsed_args.image)

        if parsed_args.all:
            data = client.images.update_tags(image.id, []).to_dict()
        else:
            parsed_args.tags = parsed_args.tags or []
            new_tags = list(set(image.tags) - set(parsed_args.tags))
            data = client.images.update_tags(image.id, new_tags).to_dict()

        data['tags'] = osc_utils.format_list(data['tags'])

        data = utils.prepare_data(data, IMAGE_FIELDS)

        return self.dict2columns(data)
