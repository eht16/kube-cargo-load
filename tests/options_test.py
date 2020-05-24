# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the Apache License, Version 2.0 license.  See the LICENSE file for details.

from unittest import mock
import sys
import unittest

from kubecargoload import _setup_options


class OptionsTest(unittest.TestCase):

    def test_option_unknown(self):
        test_argv = ['kubecargoload.py', '--unknown-option-which-will-never-exist-abcdefgh']
        with mock.patch.object(sys, 'argv', test_argv):
            with self.assertRaises(SystemExit):
                _setup_options()

    def _test_flag(self, option_short_name, option_long_name, name):
        # short name
        if option_short_name is not None:
            test_argv = ['kubecargoload.py', f'-{option_short_name}']
            with mock.patch.object(sys, 'argv', test_argv):
                arguments = _setup_options()
                self.assertTrue(getattr(arguments, name))

        # long name
        test_argv = ['kubecargoload.py', f'--{option_long_name}']
        with mock.patch.object(sys, 'argv', test_argv):
            arguments = _setup_options()
            self.assertTrue(getattr(arguments, name))

        # not set
        test_argv = ['kubecargoload.py']
        with mock.patch.object(sys, 'argv', test_argv):
            arguments = _setup_options()
            self.assertFalse(getattr(arguments, name))

    def test_flag_all_namespaces(self):
        self._test_flag('A', 'all-namespaces', 'all_namespaces')

    def test_flag_show_cpu_usage(self):
        self._test_flag('c', 'cpu', 'show_cpu_usage')

    def test_flag_debug(self):
        self._test_flag('d', 'debug', 'debug')

    def test_flag_no_header(self):
        self._test_flag('H', 'no-headers', 'no_header')

    def test_flag_version(self):
        self._test_flag('V', 'version', 'version')

    def _test_option(self, option_short_name, option_long_name, name, value):
        # short name
        if option_short_name is not None:
            test_argv = ['kubecargoload.py', f'-{option_short_name}', value]
            with mock.patch.object(sys, 'argv', test_argv):
                arguments = _setup_options()
                short_name_value = getattr(arguments, name)
                self.assertEqual(short_name_value, value)

        # long name
        test_argv = ['kubecargoload.py', f'--{option_long_name}', value]
        with mock.patch.object(sys, 'argv', test_argv):
            arguments = _setup_options()
            long_name_value = getattr(arguments, name)
            self.assertEqual(long_name_value, value)

    def test_option_context(self):
        self._test_option(None, 'context', 'context', 'my-k8s-cluster')

    def test_option_namespace(self):
        self._test_option('n', 'namespace', 'namespace', 'kube-system')

    def test_option_sort(self):
        self._test_option('s', 'sort', 'sort', 'name,namespace')

    def test_option_exclusive_group_namespace(self):
        test_argv = ['kubecargoload.py', '--namespace', 'kube-system', '--all-namespaces']
        with mock.patch.object(sys, 'argv', test_argv):
            with self.assertRaises(SystemExit):
                _setup_options()

        test_argv = ['kubecargoload.py', '-n', 'kube-system', '-A']
        with mock.patch.object(sys, 'argv', test_argv):
            with self.assertRaises(SystemExit):
                _setup_options()
