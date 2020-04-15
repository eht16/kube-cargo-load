kube-cargo-load
===============

[![PyPI](https://img.shields.io/pypi/v/kube-cargo-load.svg)](https://pypi.org/project/kube-cargo-load/)
[![Python Versions](https://img.shields.io/pypi/pyversions/kube-cargo-load.svg)](https://pypi.org/project/kube-cargo-load/)
[![License](https://img.shields.io/pypi/l/kube-cargo-load.svg)](https://pypi.org/project/kube-cargo-load/)


List Kubernetes PODs of a specific namespace or all namespaces with their
configured memory requests, limits and the current memory usage.


Features
--------

  * Overview of PODs and their memory requests, limits and actual usage
  * Provides an easy inspection of the cluster utilization in terms of memory
  * Uses `kubectl` under the hood and reuses its config
  * Supports --namespace and --all-namespaces command line arguments
  * Supports --context command line argument
    filters and column setup

Example:

    [15:09:58] enrico@host (0): ~% kubecargoload.py --all-namespaces
    Namespace   Name                                          Requests       Limits        Usage            %
    ----------------------------------------------------------------------------------------------------------
    default     kube-web-view-7c67ddb647-pvjvs                100.0 MB     100.0 MB      29.0 MB      29.00 %
    jitsi       jitsi-57d5888c88-vzrzl                          0.0  B       0.0  B     131.0 MB       0.00 %
    kube-system coredns-66bff467f8-qn4pq                       70.0 MB     170.0 MB      16.0 MB       9.41 %
    kube-system coredns-66bff467f8-znpxv                       70.0 MB     170.0 MB      13.0 MB       7.65 %
    kube-system etcd-minikube                                   0.0  B       0.0  B      43.0 MB       0.00 %
    kube-system kindnet-ptgnz                                  50.0 MB      50.0 MB      14.0 MB      28.00 %
    kube-system kube-apiserver-minikube                         0.0  B       0.0  B     275.0 MB       0.00 %
    kube-system kube-controller-manager-minikube                0.0  B       0.0  B      46.0 MB       0.00 %
    kube-system kube-proxy-s7bl8                                0.0  B       0.0  B      20.0 MB       0.00 %
    kube-system kube-scheduler-minikube                         0.0  B       0.0  B      20.0 MB       0.00 %
    kube-system metrics-server-7bc6d75975-d6sgr                 0.0  B       0.0  B      12.0 MB       0.00 %
    kube-system nginx-ingress-controller-6d57c87cb9-qpwh6       0.0  B       0.0  B      67.0 MB       0.00 %
    kube-system storage-provisioner                             0.0  B       0.0  B      21.0 MB       0.00 %
    ----------------------------------------------------------------------------------------------------------
    Summary                                                   290.0 MB     490.0 MB     707.0 MB     144.29 %


Setup
-----

### Requirements

In order to use kube-cargo-load, you will need:

- A Kubernetes cluster to connect to
- Kubernetes Metrics Server must be installed and running in Kubernetes
  (<https://github.com/kubernetes-sigs/metrics-server>)
- kubectl (it must be configured for your Kubernetes cluster)
- Python 3.6 or newer


### Installation

The easiest method is to install directly from pypi using pip:

    pip install kube-cargo-load


If you prefer, you can download kube-cargo-load and install it
directly from source:

    python setup.py install


### Download

Alternatively, you can download just the script and execute it:

    wget https://raw.githubusercontent.com/eht16/kube-cargo-load/master/kubecargoload.py
    chmod +x kubecargoload.py
    ./kubecargoload.py


Command line options
--------------------

    usage: kubecargoload.py [-h] [-A] [--context CONTEXT] [-d] [-n NAMESPACE] [-H] [-s SORT] [-V]

    optional arguments:
      -h, --help            show this help message and exit
      -A, --all-namespaces  list the requested object(s) across all namespaces (default: False)
      --context CONTEXT     the name of the kubeconfig context to use (default: None)
      -d, --debug           enable tracebacks (default: False)
      -n NAMESPACE, --namespace NAMESPACE
                            namespace to use (default: default)
      -H, --no-headers      do not print header line before the output (default: False)
      -s SORT, --sort SORT  sort by column(s), to sort by multiple columns seperate them with comma. Valid options: namespace,name,requests,limits,usage,ratio (default: namespace,name)
      -V, --version         show version and exit (default: False)


Get the Source
--------------

The source code is available at https://github.com/eht16/kube-cargo-load/.


ChangeLog
---------

### 1.0.0 / 2020-04-12

- Initial release


Contributing
------------

Found a bug or got a feature request? Please report it at
https://github.com/eht16/kube-cargo-load/issues.


Author
------

Enrico Tröger <enrico.troeger@uvena.de>
