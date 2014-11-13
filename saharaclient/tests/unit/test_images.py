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

import mock

from saharaclient.api import images
from saharaclient.tests.unit import base

import json


class ImageTest(base.BaseTestCase):
    body = {
        'username': 'name',
        'description': 'descr'
    }

    @mock.patch('requests.get')
    def test_images_list(self, mget):
        mget.return_value = base.FakeResponse(200, [self.body], 'images')

        resp = self.client.images.list()

        self.assertEqual('http://localhost:8386/images',
                         mget.call_args[0][0])
        self.assertIsInstance(resp[0], images.Image)
        self.assertFields(self.body, resp[0])

    @mock.patch('requests.get')
    def test_images_get(self, mget):
        mget.return_value = base.FakeResponse(
            200, self.body, 'image', )

        resp = self.client.images.get('id')

        self.assertEqual('http://localhost:8386/images/id',
                         mget.call_args[0][0])
        self.assertIsInstance(resp, images.Image)
        self.assertFields(self.body, resp)

    @mock.patch('requests.delete')
    def test_unregister_image(self, mdelete):
        mdelete.return_value = base.FakeResponse(204)

        self.client.images.unregister_image('id')

        self.assertEqual('http://localhost:8386/images/id',
                         mdelete.call_args[0][0])

    @mock.patch('requests.post')
    def test_update_image(self, mpost):
        mpost.return_value = base.FakeResponse(
            202, self.body, 'image')

        self.client.images.update_image('id', 'name', 'descr')

        self.assertEqual('http://localhost:8386/images/id',
                         mpost.call_args[0][0])
        self.assertEqual(self.body, json.loads(mpost.call_args[0][1]))

    @mock.patch('saharaclient.api.images.ImageManager.get')
    @mock.patch('requests.post')
    def test_update_tags(self, mpost, mget):
        mpost.return_value = base.FakeResponse(202)
        image = mock.Mock()
        mget.return_value = image

        image.tags = []
        self.client.images.update_tags('id', ['username', 'tag'])
        self.assertEqual('http://localhost:8386/images/id/tag',
                         mpost.call_args[0][0])

        image.tags = ['username', 'tag']
        self.client.images.update_tags('id', ['username'])
        self.assertEqual('http://localhost:8386/images/id/untag',
                         mpost.call_args[0][0])
