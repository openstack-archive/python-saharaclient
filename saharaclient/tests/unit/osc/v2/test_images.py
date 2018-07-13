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

import mock
from osc_lib.tests import utils as osc_utils

from saharaclient.api import images as api_images
from saharaclient.osc.v1 import images as osc_images
from saharaclient.tests.unit.osc.v1 import test_images as images_v1


IMAGE_INFO = {'id': 'id', 'name': 'image', 'username': 'ubuntu',
              'status': "Active", 'tags': ['fake', '0.1'],
              'description': 'Image for tests'}


class TestImages(images_v1.TestImages):
    def setUp(self):
        super(TestImages, self).setUp()
        self.app.api_version['data_processing'] = '2'
        self.image_mock = (
            self.app.client_manager.data_processing.images)
        self.image_mock.reset_mock()


class TestListImages(TestImages):
    def setUp(self):
        super(TestListImages, self).setUp()
        self.image_mock.list.return_value = [api_images.Image(
            None, IMAGE_INFO)]

        # Command to test
        self.cmd = osc_images.ListImages(self.app, None)

    def test_images_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Username', 'Tags']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('image', 'id', 'ubuntu', '0.1, fake')]
        self.assertEqual(expected_data, list(data))

    def test_images_list_long(self):
        arglist = ['--long']
        verifylist = [('long', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Username', 'Tags', 'Status',
                            'Description']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('image', 'id', 'ubuntu', '0.1, fake', 'Active',
                          'Image for tests')]
        self.assertEqual(expected_data, list(data))

    def test_images_list_successful_selection(self):
        arglist = ['--name', 'image', '--tags', 'fake', '--username', 'ubuntu']
        verifylist = [('name', 'image'), ('tags', ['fake']),
                      ('username', 'ubuntu')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.list.assert_called_once_with(
            search_opts={'tags': ['fake']})

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Username', 'Tags']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = [('image', 'id', 'ubuntu', '0.1, fake')]
        self.assertEqual(expected_data, list(data))

    def test_images_list_with_name_nothing_selected(self):
        arglist = ['--name', 'img']
        verifylist = [('name', 'img')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Username', 'Tags']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = []
        self.assertEqual(expected_data, list(data))

    def test_images_list_with_username_nothing_selected(self):
        arglist = ['--username', 'fedora']
        verifylist = [('username', 'fedora')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that columns are correct
        expected_columns = ['Name', 'Id', 'Username', 'Tags']
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = []
        self.assertEqual(expected_data, list(data))


class TestShowImage(TestImages):
    def setUp(self):
        super(TestShowImage, self).setUp()
        self.image_mock.find_unique.return_value = api_images.Image(
            None, IMAGE_INFO)

        # Command to test
        self.cmd = osc_images.ShowImage(self.app, None)

    def test_image_show_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_image_show(self):
        arglist = ['image']
        verifylist = [('image', 'image')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.find_unique.assert_called_once_with(name='image')

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Name', 'Status', 'Tags',
                            'Username')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ['Image for tests', 'id', 'image', 'Active',
                         '0.1, fake', 'ubuntu']
        self.assertEqual(expected_data, list(data))


class TestRegisterImage(TestImages):
    def setUp(self):
        super(TestRegisterImage, self).setUp()
        self.image_mock.update_image.return_value = mock.Mock(
            image=IMAGE_INFO.copy())
        self.app.client_manager.image = mock.Mock()
        self.image_client = self.app.client_manager.image.images
        self.image_client.get.return_value = mock.Mock(id='id')

        # Command to test
        self.cmd = osc_images.RegisterImage(self.app, None)

    def test_image_register_without_username(self):
        arglist = ['id']
        verifylist = [('image', 'id')]

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_image_register_required_options(self):
        arglist = ['id', '--username', 'ubuntu']
        verifylist = [('image', 'id'), ('username', 'ubuntu')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.update_image.assert_called_once_with(
            'id', desc=None, user_name='ubuntu')

        # Check that columns are correct
        expected_columns = ('Description', 'Id', 'Name', 'Status', 'Tags',
                            'Username')
        self.assertEqual(expected_columns, columns)

        # Check that data is correct
        expected_data = ['Image for tests', 'id', 'image', 'Active',
                         '0.1, fake', 'ubuntu']
        self.assertEqual(expected_data, list(data))

    def test_image_register_all_options(self):
        arglist = ['id', '--username', 'ubuntu', '--description', 'descr']
        verifylist = [('image', 'id'), ('username', 'ubuntu'),
                      ('description', 'descr')]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.update_image.assert_called_once_with(
            'id', desc='descr', user_name='ubuntu')


class TestUnregisterImage(TestImages):
    def setUp(self):
        super(TestUnregisterImage, self).setUp()
        self.image_mock.find_unique.return_value = api_images.Image(
            None, IMAGE_INFO)

        # Command to test
        self.cmd = osc_images.UnregisterImage(self.app, None)

    def test_image_unregister_no_options(self):
        arglist = []
        verifylist = []

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_image_unregister(self):
        arglist = ['image']
        verifylist = [('image', ['image'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.find_unique.assert_called_once_with(name='image')
        self.image_mock.unregister_image.assert_called_once_with('id')


class TestSetImageTags(TestImages):
    def setUp(self):
        super(TestSetImageTags, self).setUp()
        image_info = IMAGE_INFO.copy()
        image_info['tags'] = []
        self.image_mock.find_unique.return_value = api_images.Image(
            None, image_info)
        self.image_mock.update_tags.return_value = api_images.Image(
            None, image_info)

        # Command to test
        self.cmd = osc_images.SetImageTags(self.app, None)

    def test_image_tags_set_without_tags(self):
        arglist = ['id']
        verifylist = [('image', 'id')]

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_image_tags_set(self):
        arglist = ['image', '--tags', 'fake', '0.1']
        verifylist = [('image', 'image'), ('tags', ['fake', '0.1'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.find_unique.assert_called_with(name='image')
        self.image_mock.update_tags.assert_called_once_with(
            'id', ['fake', '0.1'])


class TestAddImageTags(TestImages):
    def setUp(self):
        super(TestAddImageTags, self).setUp()
        image_info = IMAGE_INFO.copy()
        image_info['tags'] = []
        self.image_mock.update_tags.return_value = api_images.Image(
            None, image_info)
        self.image_mock.find_unique.return_value = api_images.Image(
            None, image_info)

        # Command to test
        self.cmd = osc_images.AddImageTags(self.app, None)

    def test_image_tags_add_without_tags(self):
        arglist = ['id']
        verifylist = [('image', 'id')]

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_image_tags_add(self):
        arglist = ['image', '--tags', 'fake']
        verifylist = [('image', 'image'), ('tags', ['fake'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.find_unique.assert_called_with(name='image')
        self.image_mock.update_tags.assert_called_once_with(
            'id', ['fake'])


class TestRemoveImageTags(TestImages):
    def setUp(self):
        super(TestRemoveImageTags, self).setUp()
        self.image_mock.update_tags.return_value = api_images.Image(
            None, IMAGE_INFO)
        self.image_mock.find_unique.return_value = api_images.Image(
            None, IMAGE_INFO)

        # Command to test
        self.cmd = osc_images.RemoveImageTags(self.app, None)

    def test_image_tags_remove_both_options(self):
        arglist = ['id', '--all', '--tags', 'fake']
        verifylist = [('image', 'id'), ('all', True), ('tags', ['fake'])]

        self.assertRaises(osc_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_image_tags_remove(self):
        arglist = ['image', '--tags', 'fake']
        verifylist = [('image', 'image'), ('tags', ['fake'])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.find_unique.assert_called_with(name='image')
        self.image_mock.update_tags.assert_called_once_with(
            'id', ['0.1'])

    def test_image_tags_remove_all(self):
        arglist = ['image', '--all']
        verifylist = [('image', 'image'), ('all', True)]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # Check that correct arguments were passed
        self.image_mock.find_unique.assert_called_with(name='image')
        self.image_mock.update_tags.assert_called_once_with(
            'id', [])
