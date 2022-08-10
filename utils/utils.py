"""RHCS-System-test Utility module."""
import re
from urllib.request import urlopen
import logging

import requests
from yaml import dump, safe_load

log = logging.getLogger(__file__)


def get_config(file_name="env.yaml"):
    """Return the config yaml content in dictionary."""
    return safe_load(open(file_name).read())


def get_kubeconfig(name="qe-hive"):
    """return kubeconfig file path.

    Args:
        name: kubeconfig name
    Returns:
        kube_config_path
    """
    content = get_config()["kubeconfig"][name]
    filename = f"configs/{name}.kubeconfig"
    with open(filename, "w") as _file:
        _file.write(dump(content))
    return filename


def get_oc_builds():
    """
    This will return the latest build urls
    args:
        ocp_version : str accepted values : 4.11.0,4.12.0
        os_type : str accepted values : linux mac windows
        build_type : str accpeted values : nightly , ci
    return:
        {"client" : client_url , "installer": installer_url}
    """
    try:
        config = get_config()
        ocp_version = config["oc_builds"]["ocp_version"]
        os_type = config["oc_builds"]["os_type"]
        build_type = config["oc_builds"]["build_type"]
        url = f"https://amd64.ocp.releases.ci.openshift.org/api/v1/releasestream/{ocp_version}-0.{build_type}/latest"
        data = requests.get(url, verify=False)
        downloadURL = data.json()["downloadURL"]
        log.info(downloadURL)
        html = urlopen(downloadURL)
        text = html.read()
        plaintext = text.decode("utf8")
        links = re.findall("href=[\"'](.*?)[\"']", plaintext)
        log.info(links)
        client_url = [i for i in links if f"openshift-client-{os_type}" in i]
        installer_url = [i for i in links if f"openshift-install-{os_type}" in i]
        return {
            "client": f"{downloadURL}/{client_url[0]}",
            "installer": f"{downloadURL}/{installer_url[0]}",
        }
    except:
        log.error("Unable to fetch the build details")
        return None
