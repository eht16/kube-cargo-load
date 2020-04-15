#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This software may be modified and distributed under the terms
# of the Apache License, Version 2.0 license.  See the LICENSE file for details.

"""
List PODs of a specific namespace or all namespaces with their
configured memory requests, limits and the current memory usage.
"""

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from collections import namedtuple
from decimal import Decimal, InvalidOperation
from os.path import basename
import json
import subprocess
import sys


VERSION = '1.1'
KUBECTL_BIN = 'kubectl'

Pod = namedtuple('Pod', ('namespace', 'name', 'memory_limits', 'memory_requests', 'memory_usage'))


class KubernetesCargoLoadOverviewProvider:

    def __init__(self, namespace, context=None):
        self._namespace = namespace
        self._context = context
        self._pod_memory_usage_data = dict()
        self._pods = dict()
        self._pod_data = None

    def provide(self):
        self._fetch_pod_memory_usage()
        self._fetch_pod_data()

        return self._pods

    def _fetch_pod_memory_usage(self):
        top_pods_output = self._execute_kubectl_top_pods()
        for line in top_pods_output.splitlines():
            columns = line.strip().split()
            if len(columns) > 3:
                namespace, name, _, memory_usage_pretty = columns
            else:
                name, _, memory_usage_pretty = columns
                namespace = self._namespace

            memory_usage = self._parse_quantity(memory_usage_pretty)

            pod_key = (namespace, name)
            self._pod_memory_usage_data[pod_key] = memory_usage

    def _execute_kubectl_top_pods(self):
        return self._execute_kubectl('top', 'pods', '--no-headers=true')

    def _execute_kubectl(self, *arguments):
        command = [KUBECTL_BIN]
        command.extend(arguments)

        # context
        if self._context is not None:
            command.append('--context')
            command.append(self._context)

        # namespace
        if self._namespace is None:
            command.append('--all-namespaces')
        else:
            command.append('--namespace')
            command.append(self._namespace)

        try:
            process = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True)
        except subprocess.CalledProcessError as exc:
            print(exc.stderr.decode('utf-8'))
            raise
        else:
            return process.stdout.decode('utf-8')

    def _fetch_pod_data(self):
        get_pods_output = self._execute_kubectl_get_pods()
        pods_data = json.loads(get_pods_output)
        for self._pod_data in pods_data['items']:
            if self._pod_is_job():
                continue  # do not consider (cron) jobs

            pod = self._factor_pod()
            pod_key = (pod.namespace, pod.name)
            self._pods[pod_key] = (pod)

    def _execute_kubectl_get_pods(self):
        return self._execute_kubectl('get', 'pods', '-o', 'json')

    def _pod_is_job(self):
        labels = self._get_nested_pod_data_attribute('metadata', 'labels')
        got_job_label = 'job-name' in labels

        owner_references = self._get_nested_pod_data_attribute(
            'metadata',
            'ownerReferences',
            default=list())
        got_owner_job = False
        for owner_reference in owner_references:
            if 'kind' in owner_reference and owner_reference['kind'] == 'Job':
                got_owner_job = True
                break

        return bool(got_job_label and got_owner_job)

    def _factor_pod(self):
        namespace = self._get_nested_pod_data_attribute('metadata', 'namespace')
        name = self._get_nested_pod_data_attribute('metadata', 'name')
        memory_limits = self._get_resources('limits')
        memory_requests = self._get_resources('requests')

        pod_key = (namespace, name)
        memory_usage = self._pod_memory_usage_data.get(pod_key, Decimal(0))

        pod = Pod(
            namespace=namespace,
            name=name,
            memory_limits=memory_limits,
            memory_requests=memory_requests,
            memory_usage=memory_usage)

        return pod

    def _get_nested_pod_data_attribute(self, *keys, default=None, pod_data=None):
        value = pod_data or self._pod_data
        for key in keys:
            if key in value:
                value = value[key]
            else:
                value = default
                break

        return value

    def _get_resources(self, key):
        value = 0
        containers = self._get_nested_pod_data_attribute('spec', 'containers')
        for container in containers:
            container_value = self._get_nested_pod_data_attribute(
                'resources',
                key,
                'memory',
                pod_data=container)
            if container_value is not None:
                container_value_bytes = self._parse_quantity(container_value)
                value += container_value_bytes

        return value

    def _parse_quantity(self, quantity):  # pylint: disable=too-complex,no-self-use
        # Taken from https://github.com/kubernetes-client/python/blob/master/kubernetes/utils/quantity.py
        """
        Parse kubernetes canonical form quantity like 200Mi to a decimal number.
        Supported SI suffixes:
        base1024: Ki | Mi | Gi | Ti | Pi | Ei
        base1000: n | u | m | "" | k | M | G | T | P | E
        See https://github.com/kubernetes/apimachinery/blob/master/pkg/api/resource/quantity.go
        Input:
        quantity: string. kubernetes canonical form quantity
        Returns:
        Decimal
        Raises:
        ValueError on invalid or unknown input
        """
        if isinstance(quantity, (int, float, Decimal)):
            return Decimal(quantity)

        exponents = {"n": -3, "u": -2, "m": -1, "K": 1, "k": 1, "M": 2,
                     "G": 3, "T": 4, "P": 5, "E": 6}

        quantity = str(quantity)
        number = quantity
        suffix = None
        if len(quantity) >= 2 and quantity[-1] == "i":
            if quantity[-2] in exponents:
                number = quantity[:-2]
                suffix = quantity[-2:]
        elif len(quantity) >= 1 and quantity[-1] in exponents:
            number = quantity[:-1]
            suffix = quantity[-1:]

        try:
            number = Decimal(number)  # pylint: disable=redefined-variable-type
        except InvalidOperation:
            raise ValueError("Invalid number format: {}".format(number))

        if suffix is None:
            return number

        if suffix.endswith("i"):
            base = 1024
        elif len(suffix) == 1:
            base = 1000
        else:
            raise ValueError("{} has unknown suffix".format(quantity))

        # handly SI inconsistency
        if suffix == "ki":
            raise ValueError("{} has unknown suffix".format(quantity))

        if suffix[0] not in exponents:
            raise ValueError("{} has unknown suffix".format(quantity))

        exponent = Decimal(exponents[suffix[0]])
        return number * (base ** exponent)


class KubernetesCargoLoadOverviewPrinter:

    _format_pattern = '{:{w_namespace}} {:{w_name}} {:>{w_requests}} {:>{w_limits}} {:>{w_usage}} {:>{w_ratio}}'

    def __init__(self, overview, no_header=False, sort='namespace,name'):
        self._overview = overview
        self._no_header = no_header
        self._sort = sort
        self._column_widths = dict()
        self._pod = None
        self._sums = dict(memory_requests=0, memory_limits=0, memory_usage=0, memory_ratio=0)

    def print(self):
        self._determine_maximum_column_widths()
        self._print_header()
        self._print_separator()
        self._print_pod_data()
        self._print_separator()
        self._print_summary()

    def _determine_maximum_column_widths(self):
        max_namespace = 0
        max_name = 40
        for pod in self._overview.values():
            max_namespace = max(max_namespace, len(pod.namespace))
            max_name = max(max_name, len(pod.name))
        # consider column names as well
        max_namespace = max(max_namespace, len('Namespace'))
        max_name = max(max_name, len('Name'))

        self._column_widths['w_namespace'] = max_namespace
        self._column_widths['w_name'] = max_name
        self._column_widths['w_requests'] = 12
        self._column_widths['w_limits'] = 12
        self._column_widths['w_usage'] = 12
        self._column_widths['w_ratio'] = 12

    def _print_header(self):
        if self._no_header:
            return

        print(self._format_pattern.format(
            'Namespace',
            'Name',
            'Requests',
            'Limits',
            'Usage',
            '%',
            **self._column_widths))

    def _print_separator(self):
        if self._no_header:
            return

        print('-' * (sum(self._column_widths.values()) + len(self._column_widths)))

    def _print_pod_data(self):
        pods_sorted = sorted(self._overview.values(), key=self._get_sort_key_for_pod)
        for self._pod in pods_sorted:
            self._sums['memory_requests'] += self._pod.memory_requests
            if self._pod.memory_limits:  # consider usage for summary only if limit is set
                self._sums['memory_limits'] += self._pod.memory_limits
                self._sums['memory_usage'] += self._pod.memory_usage

            print(
                self._format_pattern.format(
                    self._pod.namespace,
                    self._pod.name,
                    self._humanize_bytes(self._pod.memory_requests),
                    self._humanize_bytes(self._pod.memory_limits),
                    self._humanize_bytes(self._pod.memory_usage),
                    self._get_memory_usage_ratio_formatted(),
                    **self._column_widths))

    def _get_sort_key_for_pod(self, pod):
        elements = list()
        for sort_key in self._sort.split(','):
            sort_key = sort_key.strip()

            if sort_key == 'name':
                elements.append(pod.name)
            elif sort_key == 'namespace':
                elements.append(pod.namespace)
            elif sort_key == 'requests':
                elements.append(pod.memory_requests)
            elif sort_key == 'limits':
                elements.append(pod.memory_limits)
            elif sort_key == 'usage':
                elements.append(pod.memory_usage)
            elif sort_key == 'ratio':
                ratio = self._get_memory_usage_ratio(pod.memory_limits, pod.memory_usage)
                elements.append(ratio)
            else:
                raise ValueError(f'Unsupported sort key: {sort_key}')

        return tuple(elements)

    def _humanize_bytes(self, bytes_, precision=1):  # pylint: disable=no-self-use
        suffixes = ['B', 'Ki', 'Mi', 'Gi', 'Ti']
        suffix_index = 0
        while bytes_ >= 1024:
            suffix_index += 1
            bytes_ = bytes_ / Decimal(1024)
        return "{:.{precision}f} {:>2}".format(bytes_, suffixes[suffix_index], precision=precision)

    def _get_memory_usage_ratio_formatted(self, maximum=None, use=None):
        ratio = self._get_memory_usage_ratio(maximum, use)
        return '{:.2f} %'.format(ratio)

    def _get_memory_usage_ratio(self, maximum=None, use=None):
        if maximum is None:
            maximum = self._pod.memory_limits
        if use is None:
            use = self._pod.memory_usage

        if not maximum:
            ratio = 0
        else:
            ratio = (use * 100) / maximum
        return ratio

    def _print_summary(self):
        print(self._format_pattern.format(
            'Summary',
            '(PODs without configured limits ignored)',
            self._humanize_bytes(self._sums['memory_requests']),
            self._humanize_bytes(self._sums['memory_limits']),
            self._humanize_bytes(self._sums['memory_usage']),
            self._get_memory_usage_ratio_formatted(
                self._sums['memory_limits'],
                self._sums['memory_usage']),
            **self._column_widths))


def _setup_options():
    argument_parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    namespace_group = argument_parser.add_mutually_exclusive_group()

    namespace_group.add_argument(
        '-A',
        '--all-namespaces',
        dest='all_namespaces',
        action='store_true',
        help='list the requested object(s) across all namespaces',
        default=False)

    argument_parser.add_argument(
        '--context',
        dest='context',
        help='the name of the kubeconfig context to use')

    argument_parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='enable tracebacks',
        default=False)

    namespace_group.add_argument(
        '-n',
        '--namespace',
        dest='namespace',
        help='namespace to use',
        default='default')

    argument_parser.add_argument(
        '-H',
        '--no-headers',
        dest='no_header',
        action='store_true',
        help='do not print header line before the output',
        default=False)

    argument_parser.add_argument(
        '-s',
        '--sort',
        dest='sort',
        help='sort by column(s), to sort by multiple columns seperate them with comma. '
             'Valid options: namespace,name,requests,limits,usage,ratio',
        default='namespace,name')

    argument_parser.add_argument(
        '-V',
        '--version',
        dest='version',
        action='store_true',
        help='show version and exit',
        default=False)

    return argument_parser.parse_args()


def main():
    options = _setup_options()
    if options.version:
        print('{} {}'.format(basename(__file__), VERSION))
        sys.exit(0)

    namespace = None if options.all_namespaces else options.namespace

    try:
        overview_provider = KubernetesCargoLoadOverviewProvider(namespace, options.context)
        overview = overview_provider.provide()

        printer = KubernetesCargoLoadOverviewPrinter(overview, options.no_header, options.sort)
        printer.print()
    except Exception as exc:  # pylint: disable=broad-except
        if options.debug:
            raise

        print(exc, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
