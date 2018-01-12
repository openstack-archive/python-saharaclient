# Copyright (c) 2013 Mirantis Inc.
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

from saharaclient.api import base


class Image(base.Resource):
    resource_name = 'Image'
    defaults = {'description': ''}


class _ImageManager(base.ResourceManager):
    resource_class = Image

    def list(self, search_opts=None):
        """Get a list of registered images."""
        query = base.get_query_string(search_opts)
        return self._list('/images%s' % query, 'images')

    def get(self, id):
        """Get information about an image"""
        return self._get('/images/%s' % id, 'image')

    def unregister_image(self, image_id):
        """Remove an Image from Sahara Image Registry."""
        self._delete('/images/%s' % image_id)

    def update_image(self, image_id, user_name, desc=None):
        """Create or update an Image in Image Registry."""
        desc = desc if desc else ''
        data = {"username": user_name,
                "description": desc}

        return self._post('/images/%s' % image_id, data)


class ImageManagerV1(_ImageManager):
    def update_tags(self, image_id, new_tags):
        """Update an Image tags.

        :param new_tags: list of tags that will replace currently
                              assigned  tags
        """
        # Do not add :param list in the docstring above until this is solved:
        # https://github.com/sphinx-doc/sphinx/issues/2549
        old_image = self.get(image_id)

        old_tags = frozenset(old_image.tags)
        new_tags = frozenset(new_tags)

        to_add = list(new_tags - old_tags)
        to_remove = list(old_tags - new_tags)

        add_response, remove_response = None, None

        if to_add:
            add_response = self._post('/images/%s/tag' % image_id,
                                      {'tags': to_add}, 'image')

        if to_remove:
            remove_response = self._post('/images/%s/untag' % image_id,
                                         {'tags': to_remove}, 'image')

        return remove_response or add_response or self.get(image_id)


class ImageManagerV2(_ImageManager):
    def get_tags(self, image_id):
        return self._get('/images/%s/tags' % image_id)

    def update_tags(self, image_id, new_tags):
        return self._update('/images/%s/tags' % image_id,
                            {'tags': new_tags})

    def delete_tags(self, image_id):
        return self._delete('/images/%s/tags' % image_id)

# NOTE(jfreud): keep this around for backwards compatibility
ImageManager = ImageManagerV1
