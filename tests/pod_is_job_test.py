# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the Apache License, Version 2.0 license.  See the LICENSE file for details.

from unittest import mock
import json
import unittest

from kubecargoload import KubernetesCargoLoadOverviewProvider


# pylint: disable=protected-access


class PodIsJobTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pod_data_with_job = None
        self._pod_data_without_owner_job = None
        self._pod_data_without_job_name = None
        self._pod_data_no_job = None

    def setUp(self):
        super().setUp()

        filename = 'tests/test_data/pods_jobs.json'
        with open(filename, encoding='utf-8') as all_pod_data_f:
            all_pod_data = json.load(all_pod_data_f)

        self._pod_data_with_job = all_pod_data['items'][0]
        self._pod_data_without_owner_job = all_pod_data['items'][1]
        self._pod_data_without_job_name = all_pod_data['items'][2]
        self._pod_data_no_job = all_pod_data['items'][3]

    def test_pod_is_job_with_job(self):
        provider = self._factor_provider()
        # test
        with mock.patch.object(provider, '_pod_data', self._pod_data_with_job):
            result = provider._pod_is_job()
        # check
        self.assertTrue(result)

    def _factor_provider(self):  # pylint: disable=no-self-use
        return KubernetesCargoLoadOverviewProvider(
            namespace=None,
            context=None,
            show_cpu_usage=None)

    def test_pod_is_job_without_owner_job(self):
        provider = self._factor_provider()
        # test
        with mock.patch.object(provider, '_pod_data', self._pod_data_without_owner_job):
            result = provider._pod_is_job()
        # check
        self.assertFalse(result)

    def test_pod_is_job_without_job_name(self):
        provider = self._factor_provider()
        # test
        with mock.patch.object(provider, '_pod_data', self._pod_data_without_job_name):
            result = provider._pod_is_job()
        # check
        self.assertFalse(result)

    def test_pod_is_job_no_job(self):
        provider = self._factor_provider()
        # test
        with mock.patch.object(provider, '_pod_data', self._pod_data_no_job):
            result = provider._pod_is_job()
        # check
        self.assertFalse(result)
