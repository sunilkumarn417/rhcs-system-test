"""Deploy OCP cluster using QE-Hive Service."""

import logging
import sys

from docopt import docopt

from lib.qehive import QEHive
from utils.utils import get_kubeconfig

LOG = logging.getLogger(__name__)

usage = """
Deploy QE-Hive OCP cluster ....
This script deploys OCP cluster(s) using QE-Hive service.
Please ensure floating IP address are created and Route53 entries are added already.

    template        QE-Hive template file
    cluster_name    Name of the cluster.
    image           OCP container image.

  Example:
    python deploy.py \
        --template templates/qe-hive/single-node-cluster/osp_sno_cluster_resources.yaml \
        --cluster-name ceph-rhosd-01 \
        --image quay.io/openshift-release-dev/ocp-release:4.10.3-x86_64

Usage:
  deploy.py (--template TEMPLATE) (--cluster-name NAME) (--image IMAGE)
  deploy.py -h | --help

Options:
  -h --help     Show this screen
"""


if __name__ == "__main__":

    logging.basicConfig(
        handlers=[logging.StreamHandler(sys.stdout)],
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    )
    _args = docopt(usage)

    template = _args["TEMPLATE"]
    image = _args["IMAGE"]
    cluster_name = _args["NAME"]

    kube_config = get_kubeconfig()
    _resources = open(template).read()
    _resources = _resources.replace("CLUSTER__NAME", cluster_name)
    _resources = _resources.replace("OCP__IMAGE", image)

    qehive = QEHive(kubeconfig=kube_config, namespace="ceph")

    qehive.deploy_ocp(_resources)
    qehive.wait_for_completion(cluster_name)

    LOG.info("---- completed ----")
