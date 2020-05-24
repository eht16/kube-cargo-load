# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the Apache License, Version 2.0 license.  See the LICENSE file for details.

from decimal import Decimal
import unittest

from ddt import data, ddt, unpack

from kubecargoload import KubernetesCargoLoadOverviewPrinter


# pylint: disable=protected-access


TEST_VARIATIONS = (
    # bytes, precision, show_cpu_usage, result
    (0, 1, False, '0.0  B'),
    (1, 1, False, '1.0  B'),
    (10, 1, False, '10.0  B'),
    (100, 1, False, '100.0  B'),
    (1000, 1, False, '1000.0  B'),
    (1023, 1, False, '1023.0  B'),

    (1024, 1, False, '1.0 Ki'),
    (1025, 1, False, '1.0 Ki'),
    (1024 * 1.04, 1, False, '1.0 Ki'),
    (1024 * 1.05, 1, False, '1.1 Ki'),

    (1024 * 1024 - 1024, 1, False, '1023.0 Ki'),
    (1024 * 1024, 1, False, '1.0 Mi'),
    (1024 * 1024 + 1, 1, False, '1.0 Mi'),
    (1024 * 1024 * 1.04, 1, False, '1.0 Mi'),
    (1024 * 1024 * 1.05, 1, False, '1.1 Mi'),
    (1024 * 1024 * 1.2 - 1, 1, False, '1.2 Mi'),

    (1024 * 1024 * 1024 - 1024 * 1024, 1, False, '1023.0 Mi'),
    (1024 * 1024 * 1024, 1, False, '1.0 Gi'),
    (1024 * 1024 * 1024 + 1, 1, False, '1.0 Gi'),
    (1024 * 1024 * 1024 * 1.04, 1, False, '1.0 Gi'),
    (1024 * 1024 * 1024 * 1.05, 1, False, '1.1 Gi'),
    (1024 * 1024 * 1024 * 1.2 - 1, 1, False, '1.2 Gi'),

    (1024 * 1024 * 1024 * 1024 - 1024 * 1024 * 1024, 1, False, '1023.0 Gi'),
    (1024 * 1024 * 1024 * 1024, 1, False, '1.0 Ti'),
    (1024 * 1024 * 1024 * 1024 + 1, 1, False, '1.0 Ti'),
    (1024 * 1024 * 1024 * 1024 * 1.04, 1, False, '1.0 Ti'),
    (1024 * 1024 * 1024 * 1024 * 1.05, 1, False, '1.1 Ti'),
    (1024 * 1024 * 1024 * 1024 * 1.2 - 1, 1, False, '1.2 Ti'),

    # precision 0
    (0, 0, False, '0  B'),
    (1024, 0, False, '1 Ki'),
    (1025, 0, False, '1 Ki'),
    (1024 * 1.04, 0, False, '1 Ki'),
    (1024 * 1.05, 0, False, '1 Ki'),
    (1024 * 1.5, 0, False, '2 Ki'),

    # precision 2
    (0, 2, False, '0.00  B'),
    (1024, 2, False, '1.00 Ki'),
    (1025, 2, False, '1.00 Ki'),
    (1024 * 1.04, 2, False, '1.04 Ki'),
    (1024 * 1.05, 2, False, '1.05 Ki'),
    (1024 * 1.5, 2, False, '1.50 Ki'),

    # cpu
    (0, 0, True, '0 m'),
    (1, 0, True, '1000 m'),
    (24, 0, True, '24000 m'),
    (1024, 0, True, '1024000 m'),
)


@ddt
class HumanizeBytesTest(unittest.TestCase):

    @data(*TEST_VARIATIONS)
    @unpack
    def test_humanize_bytes(self, bytes_, precision, show_cpu_usage, expected_result):
        printer = KubernetesCargoLoadOverviewPrinter(
            None,
            no_header=False,
            sort=None,
            show_cpu_usage=show_cpu_usage)
        # test
        result = printer._humanize_bytes(bytes_=Decimal(bytes_), precision=precision)
        # check
        self.assertEqual(result, expected_result)
