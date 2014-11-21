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

try:
    # Python2.x
    import ConfigParser as configparser
except ImportError:
    # Python 3.x
    import configparser

import collections
import logging


# In Kanzo this is more flexible, but our purpose it's enough to hardcode it
CONFIG_MULTI_PARAMETER_SEPARATOR = ','
LOG = logging.getLogger('packstack')


class Config(object):
    def __init__(self, path, meta):
        """Class used for reading/writing configuration from/to file given by
        attribute 'path'.

        Attribute 'meta' has to be dictionary. Keys of meta have to be
        in format 'section/name'. Values should be in following format:
        {'default': 'default value', 'is_multi': False,
         'processors': [func, func], 'validators': [func, func],
         'usage': 'Description'}
        """
        self._path = path
        self._meta = meta
        self._values = {}

        self._config = configparser.SafeConfigParser()
        if not self._config.read(path):
            raise ValueError('Failed to parse config file %s.' % path)

        self._get_values()
        self._validate_config()

    def save(self):
        """Saves configuration to file."""
        sections = collections.OrderedDict()
        for key in self._meta.keys():
            is_multi = self._meta[key].get('is_multi', False)
            separator = CONFIG_MULTI_PARAMETER_SEPARATOR
            value = self[key]
            if is_multi:
                value = separator.join(value)
            section, variable = key.split('/', 1)
            usage = self._meta[key].get('usage')
            options = self._meta[key].get('options')
            if options:
                usage += '\nValid values: %s' % ', '.join(options)
            sections.setdefault(section, []).append((variable, value, usage))

        fmt = '\n%(usage)s\n%(variable)s=%(value)s\n'
        with open(self._path, 'w') as confile:
            for section, variables in sections.items():
                confile.write('\n[%(section)s]' % locals())
                for variable, value, usage in variables:
                    usage = usage or ''
                    usage = textwrap.fill(usage, initial_indent='# ',
                                          subsequent_indent='# ',
                                          break_long_words=False)
                    confile.write(fmt % locals())

    def _validate_value(self, key, value):
        metadata = self._meta[key]
        # split multi value
        is_multi = metadata.get('is_multi', False)
        if is_multi:
            separator = CONFIG_MULTI_PARAMETER_SEPARATOR
            value = [i.strip() for i in value.split(separator) if i]
        else:
            value = [value]
        options = metadata.get('options')
        # process value
        new_value = []
        for val in value:
            nv = val
            for fnc in metadata.get('processors', []):
                nv = fnc(nv, key=key, config=self)
                LOG.debug('Parameter processor %s(%s, key=%s) changed '
                          'value.' % (fnc.func_name, val, key))
            new_value.append(nv)
        value = new_value
        # validate value
        for val in value:
            if options and val not in options:
                raise ValueError('Value of parameter %s is not from valid '
                                 'values %s: %s' % (key, options, val))
            for fnc in metadata.get('validators', []):
                try:
                    fnc(val, key=key, config=self)
                except ValueError:
                    LOG.debug('Parameter validator %s(%s, key=%s) failed '
                              'validation.' % (fnc.func_name, val, key))
                    raise
        return value if is_multi else value.pop()

    def _validate_config(self):
        for key in self._meta:
            self._values[key] = self._validate_value(key, self._values[key])

    def __getitem__(self, key):
        return self._values[key]

    def _get_values(self):
        for key in self._meta:
            section, variable = key.split('/', 1)
            try:
                value = self._config.get(section, variable)
            except (configparser.NoOptionError, configparser.NoSectionError):
                value = self._meta[key].get('default', '')
            self._values[key] = value

    def __setitem__(self, key, value):
        try:
            metadata = self._meta[key]
        except KeyError:
            raise KeyError('Given key %s does not exist in metadata '
                           'dictionary.' % key)
        # process and validate new value
        self._values[key] = self._validate_value(key, value)

    def __contains__(self, item):
        return item in self._meta

    def __iter__(self):
        return iter(self._meta.keys())

    def keys(self):
        return self._meta.keys()

    def values(self):
        return self._values.values()

    def items(self):
        return self._values.items()

    def meta(self, key):
        """Returns metadata for given parameter."""
        return self._meta[key]

    def get_validated(self, key):
        return self._validate_value(key, self._values[key])
