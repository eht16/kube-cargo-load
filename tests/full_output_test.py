# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the Apache License, Version 2.0 license.  See the LICENSE file for details.

from os.path import join
from unittest import mock
import sys
import unittest

from ddt import data, ddt, unpack

from kubecargoload import KubernetesCargoLoadOverviewProvider
from kubecargoload import main as kubecargoload_main


# pylint: disable=line-too-long


TEST_VARIATIONS = (
    # output name, sys.argv, pods.json, pods.top
    ('output_cpu', ['--cpu', '--all-namespaces'], 'pods.json', 'pods.top'),
    ('output_cpu_default', ['--cpu', '--namespace', 'default'], 'pods_default.json', 'pods_default.top'),
    ('output_cpu_default_no_header', ['--cpu', '--no-headers', '--namespace', 'default'], 'pods_default.json', 'pods_default.top'),
    ('output_cpu_no_header', ['--cpu', '--no-headers'], 'pods.json', 'pods.top'),
    ('output_memory', ['--all-namespaces'], 'pods.json', 'pods.top'),
    ('output_memory_default', ['--namespace', 'default'], 'pods_default.json', 'pods_default.top'),
    ('output_memory_default_no_header', ['--no-headers', '--namespace', 'default'], 'pods_default.json', 'pods_default.top'),
    ('output_memory_default_no_header_sort_by_requests_limits', ['--no-headers', '--namespace', 'default', '--sort', 'requests,limits'], 'pods_default.json', 'pods_default.top'),
    ('output_memory_default_sort_by_requests_limits', ['--namespace', 'default', '--sort', 'requests,limits'], 'pods_default.json', 'pods_default.top'),
    ('output_memory_no_header', ['--all-namespaces', '--no-headers'], 'pods.json', 'pods.top'),
    ('output_memory_no_header_sort_by_requests_limits', ['--all-namespaces', '--no-headers', '--sort', 'requests,limits'], 'pods.json', 'pods.top'),
    ('output_memory_sort_by_requests_limits', ['--all-namespaces', '--sort', 'requests,limits'], 'pods.json', 'pods.top'),
)


@ddt
class FullOutputTest(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.maxDiff = None  # pylint: disable=invalid-name

    @data(*TEST_VARIATIONS)
    @unpack
    @mock.patch.object(KubernetesCargoLoadOverviewProvider, '_execute_kubectl_get_pods')
    @mock.patch.object(KubernetesCargoLoadOverviewProvider, '_execute_kubectl_top_pods')
    def test_full_output(self, output_name, argv, pods_json, pods_top, mocked_top_pods, mocked_get_pods):
        pods_json_content = self._read_file_contents(pods_json)
        pods_top_content = self._read_file_contents(pods_top)
        expected_output = self._read_file_contents(output_name)

        mocked_top_pods.return_value = pods_top_content
        mocked_get_pods.return_value = pods_json_content

        # mock sys.argv command line arguments
        with mock.patch.object(sys, 'argv', ['kubecargoload.py'] + argv):
            kubecargoload_main()
        # check
        output = sys.stdout.getvalue()  # pylint: disable=no-member
        self.assertEqual(output, expected_output)

    def _read_file_contents(self, filename):  # pylint: disable=no-self-use
        path = join('tests/test_data', filename)
        with open(path, encoding='utf-8') as file_h:
            return file_h.read()
