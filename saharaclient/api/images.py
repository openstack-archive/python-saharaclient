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


class ImageManager(base.ResourceManager):
    resource_class = Image

    def list(self, search_opts=None):
        query = base.get_query_string(search_opts)
        return self._list('/images%s' % query, 'images')

    def get(self, id):
        return self._get('/images/%s' % id, 'image')

    def unregister_image(self, image_id):
        self._delete('/images/%s' % image_id)

    def update_image(self, image_id, user_name, desc):
        body = {"username": user_name,
                "description": desc}

        resp = self.api.post('/images/%s' % image_id, json=body)
        if resp.status_code != 202:
            raise RuntimeError('Failed to register image %s' % image_id)

    def update_tags(self, image_id, new_tags):
        old_image = self.get(image_id)

        old_tags = frozenset(old_image.tags)
        new_tags = frozenset(new_tags)

        to_add = list(new_tags - old_tags)
        to_remove = list(old_tags - new_tags)

        if len(to_add) != 0:
            resp = self.api.post('/images/%s/tag' % image_id,
                                 json={'tags': to_add})

            if resp.status_code != 202:
                raise RuntimeError('Failed to add tags to image %s' % image_id)

        if len(to_remove) != 0:
            resp = self.api.post('/images/%s/untag' % image_id,
                                 json={'tags': to_remove})

            if resp.status_code != 202:
                raise RuntimeError('Failed to remove tags from image %s' %
                                   image_id)
