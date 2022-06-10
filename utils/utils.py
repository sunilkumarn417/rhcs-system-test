"""RHCS-System-test Utility module."""
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
