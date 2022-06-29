import logging

from kubernetes import config
from openshift.dynamic import DynamicClient

LOG = logging.getLogger(__name__)


class OpenShiftRestClient:
    def __init__(self, kubeconfig, namespace="ceph"):
        """Initialize Openshift rest client.

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

    def get_resource_object(self, api_version, kind):
        """Return custom resource object.

        Args:
            api_version: resource api version (example: hive.openshift.io/v1)
            kind: resource name (example: clusterPool|service|secret)
        Returns:
            object
        """
        for name, args in self.custom_resources.items():
            if name == kind and api_version == args["api-version"]:
                return args["object"]
        _object = self.client.resources.get(api_version=api_version, kind=kind)
        LOG.debug(f"{api_version}/{kind} resource found.")
        self.custom_resources[kind] = {
            "api-version": api_version,
            "object": _object,
        }
        return _object

    def create(self, content):
        """Create resource.

        Args:
            content: api content in dict
        Returns:
            response
        """
        api_version = content["apiVersion"]
        kind = content["kind"]
        obj = self.get_resource_object(api_version=api_version, kind=kind)
        response = obj.create(body=content, namespace=self.namespace)
        LOG.info(
            f"{kind}/{api_version}/{response['metadata']['name']} object created successfully."
        )
        LOG.debug(f"Object create response: {response}")
        return response

    def delete(self, name, api_version, kind):
        """delete resource.

        Args:
            name: resource name
            api_version: resource API version
            kind: kind of resource
        Returns:
            response
        """
        obj = self.get_resource_object(api_version=api_version, kind=kind)
        response = obj.delete(name=name, namespace=self.namespace)
        LOG.info(f"{kind}/{api_version}/{name} object deleted successfully")
        LOG.debug(f"Object delete response: {response}")
        return response
