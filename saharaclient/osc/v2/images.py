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

from saharaclient.osc.v1 import images as images_v1

IMAGE_FIELDS = ['name', 'id', 'username', 'tags', 'status', 'description']


class ListImages(images_v1.ListImages):
    """Lists registered images"""

    log = logging.getLogger(__name__ + ".ListImages")


class ShowImage(images_v1.ShowImage):
    """Display image details"""

    log = logging.getLogger(__name__ + ".ShowImage")


class RegisterImage(images_v1.RegisterImage):
    """Register an image"""

    log = logging.getLogger(__name__ + ".RegisterImage")


class UnregisterImage(images_v1.UnregisterImage):
    """Unregister image(s)"""

    log = logging.getLogger(__name__ + ".RegisterImage")


class SetImageTags(images_v1.SetImageTags):
    """Set image tags (Replace current image tags with provided ones)"""

    log = logging.getLogger(__name__ + ".AddImageTags")


class AddImageTags(images_v1.AddImageTags):
    """Add image tags"""

    log = logging.getLogger(__name__ + ".AddImageTags")


class RemoveImageTags(images_v1.RemoveImageTags):
    """Remove image tags"""

    log = logging.getLogger(__name__ + ".RemoveImageTags")
