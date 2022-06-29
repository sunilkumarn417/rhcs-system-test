"""RHCS-System-test Utility module."""
from random import choices
from string import ascii_lowercase, digits

from yaml import dump, safe_load


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


def generate_random_name(length=6):
    """Return random name."""
    return "".join(choices(ascii_lowercase + digits, k=length))
