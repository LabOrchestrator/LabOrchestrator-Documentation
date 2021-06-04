\pagebreak


# Installation

## Prerequisites

### Kubernetes Development Installation

To run %project_name% you need an instance of Kubernetes. If you want to use VMs instead of containers you additionally need to install KubeVirt.

For development we use minikube. To install minikube install docker and [kvm2](https://minikube.sigs.k8s.io/docs/drivers/kvm2/)^[https://minikube.sigs.k8s.io/docs/drivers/kvm2/] or some other driver for VMs and follow [this guide](https://minikube.sigs.k8s.io/docs/start/)^[https://minikube.sigs.k8s.io/docs/start/]. Also install `kubectl` using [this guide](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)^[https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/].

After the installation you should be able to start minikube with the command `minikube start` and get access to the cluster with `kubectl get po -A`. The command `minikube dashboard` starts a dashboard, where you can inspect your cluster on a local website. If you like you can start it with this command in the background: `nohup minikube dashboard >/dev/null 2>/dev/null &`, but then it's only possible to stop the dashboard by stopping minikube with `minikube stop`.

Start one cluster with docker `minikube start --driver=docker` and a second cluster with `minikube start -p kubevirt --driver=kvm2`. You should now see both profiles running with `minikube profile list`. [@minikubekubevirt]

`kubectl` is now configured to use more than one cluster. There should be two contexts in `kubectl config view`: `docker` and `kubevirt`. You can use the minikube kubectl command like this to specify which cluster you would like to use: `minikube kubectl get pods -p docker` and `minikube kubectl get vms -p kubevirt`. Or you can specify the context in kubectl like this: `kubectl get pods --context docker` and `kubectl get vms --context kubevirt`.

It may be sufficient to only run one cluster with kvm2 driver and execute docker inside kvm. This needs to be tested in the prototype.

### Kubernetes Productive Installation
<!-- TODO -->

### Krew and KubeVirt Installation
Install Krew using [this guide](https://krew.sigs.k8s.io/docs/user-guide/setup/install/)^[https://krew.sigs.k8s.io/docs/user-guide/setup/install/].

If you are running Minikube, use this installation guide to install KubeVirt and then Virtctl with Krew: [KubeVirt quickstart with Minikube](https://kubevirt.io/quickstart_minikube/)^[https://kubevirt.io/quickstart_minikube/]. This adds some commands to kubectl for example `kubectl get vms` instead of `kubectl get pods`.

Start kubevirt in the kubevirt cluster: `minikube -p kubevirt addon enable`. After that deploy a test VM using this guide: [Use KubeVirt](https://kubevirt.io/labs/kubernetes/lab1)^[https://kubevirt.io/labs/kubernetes/lab1]

## %project_name% Installation
<!-- TODO -->

\vfill
