"""This module exercise simple storage lifecycle as in below steps.

1) create a PVC - ( example: 5GB)
2) write data - ( example: 40/50Mb )
3) take a 2 snapshots, - ( example: snap1 , snap2)
4) delete 1 snapshot,  - ( example: delete snap1)
5) repeat the above step[2-4] for 100 times.
6) modify the volume properties.
7) perform step 4 again - all snapshots should be deleted(one snapshot at a time).
8) delete the volume.
"""

import logging
import sys
from copy import deepcopy
from time import sleep

from docopt import docopt
from yaml import safe_load, safe_load_all

from lib.openshift_client import OpenShiftRestClient
from utils.utils import generate_random_name, get_kubeconfig

LOG = logging.getLogger(__name__)

usage = """
Run continuous storage operations in a single thread.

    name            test-run name   -   Optional.
    kube-config     kube config name as in the env.yaml -  Required.
    pvc-size        Size of the Persistent volume Claim - Required.        
    storage-class   storage class to be used   -    Optional.
    snapshot-class  snapshot class name     -   Optional.
    namespace       OCP cluster namespace   -   Optional. 

  Example:
    python test_run_single_thread.py \
        --name test-run-01 \
        --pvc-size  5GB \
        --kubeconfig ocp1 \
        --storage-class ocs-external-storagecluster-ceph-rbd \
        --snapshot-class ocs-external-storagecluster-rbdplugin-snapclass \
        --namespace openshift-client \
        --log-level info

Usage:
  test_run_single_thread.py
        (--pvc-size SIZE) 
        (--kube-config KUBE_CRED)
        [--namespace <NAMESPACE>]
        [--storage-class <STORAGECLASS>]
        [--snapshot-class <SNAPSHOTCLASS>]
        [--name <NAME>]
        [--log-level <LEVEL>]
  test_run_single_thread.py -h | --help

Options:
  -h --help                         Show this screen
  --pvc-size SIZE                   pvc size
  --kube-config KUBE_CRED           kube-config name
  --namespace <NAMESPACE>           OCP cluster namespace
                                    [default: openshift-storage]
  --storage-class <STORAGECLASS>    storage class name
                                    [default: ocs-external-storagecluster-ceph-rbd]
  --snapshot-class <STORAGECLASS>   snapshot class name
                                    [default: ocs-external-storagecluster-rbdplugin-snapclass]
  --name <NAME>                     test run name
  --log-level <LEVEL>               log level name
                                    [default: info]
"""


class SingleThread:
    def __init__(self, args):
        """Initialize single thread.

        Args:
            args: arguments
        """
        self.args = args
        self.pvc_size = args["--pvc-size"]
        self.kube_config = get_kubeconfig(name=args["--kube-config"])
        self.namespace = args.get("--namespace")
        self.storage_class = args.get("--storage-class")
        self.snapshot_class = args.get("--snapshot-class")
        self.test_run_name = self.name()
        self.client = OpenShiftRestClient(
            kubeconfig=self.kube_config, namespace=self.namespace
        )

    def name(self):
        name = "test-run-"
        if self.args.get("--name"):
            name = f"{self.args['name']}-"
        return name + generate_random_name()

    def create_snapshot(self, num=1):
        """Create a {num} number of snapshots.

        Args:
            num: number of snapshots
        Returns:
            list of snapshot names
        """
        snapshot_data = open("templates/snapshot.yaml").read()
        snapshot_name = f"{self.test_run_name}-snapshot-{generate_random_name()}"
        names = []

        for snap in range(num):
            name = f"{snapshot_name}-{snap}"
            data = deepcopy(snapshot_data)
            data = (
                data.replace("NAME_SPACE", self.namespace)
                .replace("SNAPSHOT_CLASS", self.snapshot_class)
                .replace("RUN_NAME", self.test_run_name)
                .replace("SNAPSHOT_NAME", name)
            )
            data = safe_load(data)
            names.append(data)
            self.client.create(data)

        return names

    def delete_snapshot(self, content):
        """Delete a snapshot."""
        self.client.delete(
            name=content["metadata"]["name"],
            api_version=content["apiVersion"],
            kind=content["kind"],
        )

    def execute(self):
        """Execute single thread exercise."""

        # deploy pvc and pod client
        data = open("templates/pvc-pod.yaml").read()
        data = (
            data.replace("RUN_NAME", self.test_run_name)
            .replace("STORAGE_CLASS", self.storage_class)
            .replace("STORAGE_SIZE", self.pvc_size)
            .replace("NAME_SPACE", self.namespace)
        )
        data = safe_load_all(data)
        for res in data:
            self.client.create(res)

        # create 2 snapshots and delete one
        snapshots = list()
        for i in range(100):
            sleep(10)
            _snapshots = self.create_snapshot(num=2)
            sleep(5)
            self.delete_snapshot(_snapshots.pop())
            snapshots.extend(_snapshots)

        # delete all snapshots
        for i in snapshots:
            self.delete_snapshot(i)


if __name__ == "__main__":
    _args = docopt(usage)
    logging.basicConfig(
        handlers=[logging.StreamHandler(sys.stdout)],
        level=getattr(logging, _args["--log-level"].upper()),
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )
    run = SingleThread(args=_args)
    run.execute()

    LOG.info("---- completed ----")
