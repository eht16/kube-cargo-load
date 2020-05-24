# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the Apache License, Version 2.0 license.  See the LICENSE file for details.

from unittest import mock
import json
import unittest

from kubecargoload import KubernetesCargoLoadOverviewProvider


# pylint: disable=protected-access


class GetNestedPodDataAttributeTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pod_data = None

    def setUp(self):
        super().setUp()

        filename = 'tests/test_data/pods.json'
        with open(filename) as all_pod_data_f:
            all_pod_data = json.load(all_pod_data_f)

        self._pod_data = all_pod_data['items'][0]

    def test_get_nested_pod_data_attribute_flat(self):
        provider = self._factor_provider()
        # test
        result = provider._get_nested_pod_data_attribute('kind', pod_data=self._pod_data)
        # check
        expected_result = 'Pod'
        self.assertEqual(result, expected_result)

    def _factor_provider(self):  # pylint: disable=no-self-use
        return KubernetesCargoLoadOverviewProvider(
            namespace=None,
            context=None,
            show_cpu_usage=None)

    def test_get_nested_pod_data_attribute_nested(self):
        provider = self._factor_provider()
        # test
        result = provider._get_nested_pod_data_attribute(
            'spec', 'schedulerName',
            pod_data=self._pod_data)
        # check
        expected_result = 'default-scheduler'
        self.assertEqual(result, expected_result)

    def test_get_nested_pod_data_attribute_flat_default(self):
        provider = self._factor_provider()
        default = 'default-for-nonexistent-key'
        # test
        result = provider._get_nested_pod_data_attribute(
            'non-nonexistent-key',
            default=default,
            pod_data=self._pod_data)
        # check
        expected_result = default
        self.assertEqual(result, expected_result)

    def test_get_nested_pod_data_attribute_nested_default(self):
        provider = self._factor_provider()
        default = 'default-for-nonexistent-key'
        # test
        result = provider._get_nested_pod_data_attribute(
            'spec', 'nested-non-nonexistent-key',
            default=default,
            pod_data=self._pod_data)
        # check
        expected_result = default
        self.assertEqual(result, expected_result)

    def test_get_nested_pod_data_attribute_nested_default_ex(self):
        provider = self._factor_provider()
        default = 'default-for-nonexistent-key'
        # test
        result = provider._get_nested_pod_data_attribute(
            'non-nonexistent-key', 'nested-non-nonexistent-key',
            default=default,
            pod_data=self._pod_data)
        # check
        expected_result = default
        self.assertEqual(result, expected_result)

    def test_get_nested_pod_data_attribute_empty_pod_data(self):
        provider = self._factor_provider()
        default = 'default-for-nonexistent-key'
        # test
        with mock.patch.object(provider, '_pod_data', dict()):
            result = provider._get_nested_pod_data_attribute(
                'non-nonexistent-key', 'nested-non-nonexistent-key',
                default=default)
        # check
        expected_result = default
        self.assertEqual(result, expected_result)

    def test_get_nested_pod_data_attribute_empty_pod_data_passed(self):
        provider = self._factor_provider()
        default = 'default-for-nonexistent-key'
        # test
        with mock.patch.object(provider, '_pod_data', dict()):
            result = provider._get_nested_pod_data_attribute(
                'non-nonexistent-key', 'nested-non-nonexistent-key',
                default=default,
                pod_data=dict())
        # check
        expected_result = default
        self.assertEqual(result, expected_result)
