# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Red Hat, Inc.
#
# Author: Martin Magr <mmagr@redhat.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
from unittest import TestCase

from packstack.config import Config


def change_processor(value, key, config):
    if value == 'changeme':
        return 'changedvalue'
    return value

def invalid_validator(value, key, config):
    if value == 'invalid':
        raise ValueError('Value is invalid')


class ConfigTestCase(TestCase):
    def setUp(self):
        self._path = os.path.join(os.path.dirname(__file__), 'config.txt')
        meta = {
            'default1/var': {'default': '3'},
            'default2/arr': {'default': '1,2,3', 'is_multi': True},
            'test/var': {'default': '3'},
            'test/arr': {'default': '1,2,3', 'is_multi': True},
            'test/processor': {'processors': [change_processor]},
            'test/processor_multi': {
                'processors': [change_processor], 'is_multi': True
            },
        }
        self._config = Config(self._path, meta)

    def test_defaults(self):
        """[Config] Test default value behaviour"""
        self.assertEquals(self._config['default1/var'], '3')
        self.assertEquals(self._config['default2/arr'], ['1', '2', '3'])

    def test_values(self):
        """[Config] Test value fetching from file"""
        self.assertEquals(self._config['test/var'], 'a')
        self.assertEquals(self._config['test/arr'], ['a', 'b', 'c'])

    def test_processor(self):
        """[Config] Test parameter processor calling"""
        self.assertEquals(self._config['test/processor'], 'changedvalue')
        self.assertEquals(
            self._config['test/processor_multi'],
            ['original', 'changedvalue', 'unchanged']
        )

    def test_validator(self):
        """[Config] Test parameter validator calling"""
        meta = {'test/validator1': {'validators': [invalid_validator]}}
        self.assertRaises(ValueError, Config, self._path, meta)

        meta = {'test/validator2': {'validators': [invalid_validator]}}
        config = Config(self._path, meta)
        self.assertEquals(config['test/validator2'], 'valid')

        meta = {
            'test/validator3': {
                'validators': [invalid_validator],
                'is_multi': True
            }
        }
        self.assertRaises(ValueError, Config, self._path, meta)

        meta = {
            'test/validator4': {
                'validators': [invalid_validator],
                'is_multi': True
            }
        }
        config = Config(self._path, meta)
        self.assertEquals(config['test/validator4'], ['all', 'valid'])

    def test_options(self):
        """[Config] Test options"""
        meta = {'test/options1': {'options': ['1', '2', '3']}}
        config = Config(self._path, meta)
        self.assertEquals(config['test/options1'], '2')

        meta = {'test/options2': {'options': ['1', '2', '3']}}
        self.assertRaises(ValueError, Config, self._path, meta)

        meta = {
            'test/options3': {
                'options': ['1', '2', '3'],
                'is_multi': True
                }
        }
        config = Config(self._path, meta)
        self.assertEquals(config['test/options3'], ['2', '3'])

        meta = {
            'test/options4': {
                'options': ['1', '2', '3'],
                'is_multi': True
                }
        }
        self.assertRaises(ValueError, Config, self._path, meta)
