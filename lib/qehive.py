"""Module to access QE-Hive."""
import logging
from datetime import datetime, timedelta
from time import sleep

from kubernetes import config
from openshift.dynamic import DynamicClient
from yaml import safe_load

LOG = logging.getLogger(__name__)


class QEHive:
    def __init__(self, kubeconfig, namespace="ceph"):
        """Initialize QE-Hive access.

        Custom resource dictionary dynamically holds up the resource name
        and its API version. A new resource with API version would be stored
        used for next calls.


        Example::

            {
                "clusterPool":
                    {
                        "api-version": "hive.openshift.io/v1",
                         "object": pool_obj,
                    }
                "Secret":
                    {
                        "api-version": "v1",
                        "object": secret_obj,
                    }
            }

        Args:
            kubeconfig: kubeconfig file path
            namespace: QE-hive namespace ( default: ceph )
        """
        self.kcpath = kubeconfig
        self.namespace = namespace
        self.k8s_client = config.new_client_from_config(kubeconfig)
        self.client = DynamicClient(self.k8s_client)
        self.custom_resources = {}

    def get_resource_object(self, api_version, resource):
        """Return custom resource object.

        Args:
            api_version: resource api version (example: hive.openshift.io/v1)
            resource: resource name (example: clusterPool|service|secret)
        Returns:
            object
        """
        for name, args in self.custom_resources.items():
            if name == resource and api_version == args["api-version"]:
                return args["object"]
        _object = self.client.resources.get(api_version=api_version, kind=resource)
        self.custom_resources[resource] = {
            "api-version": api_version,
            "object": _object,
        }
        return _object

    def wait_for_completion(self, cluster_name, timeout=3600):
        """wait for clusterPool deployment completion.

        Args:
            cluster_name: ocp-cluster name
            timeout: timeout in seconds
        """
        pool_res = self.get_resource_object("hive.openshift.io/v1", "ClusterPool")
        cluster_pool = f"{cluster_name}-pool"

        end_time = datetime.now() + timedelta(seconds=timeout)
        while end_time > datetime.now():
            sleep(60)
            resp = pool_res.get(name=cluster_pool, namespace=self.namespace).to_dict()
            if resp["status"]["ready"]:
                LOG.info(
                    f"""cluster pool({cluster_pool}) is ready for claim....
                    After claim, Run 'rhcs-system-ceph/creds.sh' for OCP access details..."""
                )
                return
            LOG.info(f"wait for 60 seconds...\ncluster status: {resp['status']}")

        raise Exception(
            f"""Cluster is not yet ready!!! please manually check the status 
            and observe the cluster pool({cluster_pool}) logs......."""
        )

    def deploy_ocp(self, resources):
        """Deploy QE Hive resources.

        Args:
            resources: template file path
        """
        data = safe_load(resources)
        for cr in data["items"]:
            try:
                res_obj = self.get_resource_object(
                    api_version=cr["apiVersion"], resource=cr["kind"]
                )
                res_obj.create(body=cr, namespace=self.namespace)
            except Exception as err:  # noqa
                LOG.error(f"Exception occurred - {err}")
                raise Exception(err)
