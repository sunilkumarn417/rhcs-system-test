#!/usr/bin/env bash
 
claim=$1
ns="$(oc get clusterclaim $claim -o jsonpath='{.spec.namespace}')"
echo "Web Console:"
echo "========================================================================"
oc -n $ns get cd $ns -o jsonpath='{ .status.webConsoleURL }'
 
echo ""
echo ""
echo "Credentials:"
echo "========================================================================"
oc extract -n $ns secret/$(oc -n $ns get cd $ns -o jsonpath='{.spec.clusterMetadata.adminPasswordSecretRef.name}') --to=-
 
echo ""
echo ""
echo "Kubeconfig:"
echo "========================================================================"
oc extract -n $ns secret/$(oc -n $ns get cd $ns -o jsonpath='{.spec.clusterMetadata.adminKubeconfigSecretRef.name}') --to=-
