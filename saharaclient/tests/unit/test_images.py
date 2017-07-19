# Copyright (c) 2014 Mirantis Inc.
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

from saharaclient.api import images
from saharaclient.tests.unit import base

from oslo_serialization import jsonutils as json


class ImageTest(base.BaseTestCase):
    body = {
        'username': 'name',
        'description': 'descr'
    }

    def test_images_list(self):
        url = self.URL + '/images'
        self.responses.get(url, json={'images': [self.body]})

        resp = self.client.images.list()

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp[0], images.Image)
        self.assertFields(self.body, resp[0])

    def test_images_get(self):
        url = self.URL + '/images/id'
        self.responses.get(url, json={'image': self.body})

        resp = self.client.images.get('id')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertIsInstance(resp, images.Image)
        self.assertFields(self.body, resp)

    def test_unregister_image(self):
        url = self.URL + '/images/id'
        self.responses.delete(url, status_code=204)

        self.client.images.unregister_image('id')

        self.assertEqual(url, self.responses.last_request.url)

    def test_update_image(self):
        url = self.URL + '/images/id'
        self.responses.post(url, json={'image': self.body}, status_code=202)

        self.client.images.update_image('id', 'name', 'descr')

        self.assertEqual(url, self.responses.last_request.url)
        self.assertEqual(self.body,
                         json.loads(self.responses.last_request.body))

    def test_update_tags(self):
        url = self.URL + '/images/id'
        tag_url = self.URL + '/images/id/tag'
        untag_url = self.URL + '/images/id/untag'

        body = self.body.copy()
        body['tags'] = ['fake', '0.1']

        self.responses.post(tag_url, json={'image': body},
                            status_code=202)
        self.responses.post(untag_url, json={'image': body},
                            status_code=202)
        self.responses.get(url, json={'image': body})

        resp = self.client.images.update_tags('id', ['username', 'tag'])
        self.assertIsInstance(resp, images.Image)
        self.assertFields(self.body, resp)

        resp = self.client.images.update_tags('id', ['username'])
        self.assertIsInstance(resp, images.Image)
        self.assertFields(self.body, resp)
