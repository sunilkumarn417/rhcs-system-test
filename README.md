# RHCS-SYSTEM-TEST

RHCS-System-Test enables the RHCeph-ODF-OCP environment for system test scenarios.


#### Installation

Please ensure below pre-requisites are installed.
- python3.6
- virtualenv
```
# python3 -m venv <path-to-virtualenv>
# source <path-to-virtualenv>/bin/activate
```
- Get repository.
```
# git clone https://github.com/sunilkumarn417/rhcs-system-test.git
# cd rhcs-system-test
# pip install -r requirements.txt
```
- Create env.yaml and update access configurations.
```
# ===============
#    IMPORTANT
# ===============
# All portal configuration would situate here.
# QE_HIVE kubeconfig is necessary, add it under kubeconfig --> qe-hive.
# Copy this template file as env.yaml under rhcs-system-test directory, this would be
#  used by python modules to access QE-HIVE...

# ------------------------------ KUBCONFIG -------------------------------
# Very much needed
# ------------------------------------------------------------------------
kubeconfig:
    qe-hive:
        apiVersion: v1
        clusters:
        -   cluster:
                certificate-authority-data: example---abcdefghi==
                server: https://x.x.x.x:6443
            name: example.local
        contexts:
        -   context:
                cluster: example.local
                namespace: ceph-example
                user: ceph-example
            name: ceph@example.local
        current-context: local@example.local
        kind: Config
        users:
        -   name: ceph-example
            user:
                token: token-id-abcdef12345
```

### Openstack
The secrets can retrievable using `OC` commands and they are stored in the `<openstack>-<project-name>` format.

`oc get secret -n ceph`

**Note:** Only this secret name(s) should be used in the template(s).

### Directory structure

- `lib`   -   all libraries would be found here.
- `templates` -   all OCP deployment templates would be found here. 

#### Supported operations

- Deploy
```
Example:
# python deploy.py --template templates/qe-hive/single-node-cluster/osp_sno_cluster_resources.yaml --cluster-name ceph-rhosd-01 --image quay.io/openshift-release-dev/ocp-release:4.10.3-x86_64
```
