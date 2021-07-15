\pagebreak


# Installation

## Prerequisites

**TLDR**:

- [Install Minikube with kvm2](https://minikube.sigs.k8s.io/docs/start/)^[https://minikube.sigs.k8s.io/docs/start/]
- [Install kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)^[https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/]
- `minikube start --driver kvm2 --memory=8192 --cpus=4 --disk-size=50g --cni=calico`
- [Install Helm](https://helm.sh/docs/intro/install/)^[https://helm.sh/docs/intro/install/]
- [Install Krew](https://krew.sigs.k8s.io/docs/user-guide/setup/install/)^[https://krew.sigs.k8s.io/docs/user-guide/setup/install/]
- [Install KubeVirt](https://kubevirt.io/quickstart_minikube/)^[https://kubevirt.io/quickstart_minikube/]
- Install Virtctl with Krew
- [Install CDI](https://kubevirt.io/user-guide/operations/containerized_data_importer/#install-cdi)^[https://kubevirt.io/user-guide/operations/containerized_data_importer/#install-cdi]

### Kubernetes Development Installation

To run %project_name% you need an instance of Kubernetes. If you want to use VMs instead of containers you additionally need to install KubeVirt.

For development we use minikube. To install minikube install docker and [kvm2](https://minikube.sigs.k8s.io/docs/drivers/kvm2/)^[https://minikube.sigs.k8s.io/docs/drivers/kvm2/] or some other driver for VMs and follow [this guide](https://minikube.sigs.k8s.io/docs/start/)^[https://minikube.sigs.k8s.io/docs/start/]. Also install `kubectl` using [this guide](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)^[https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/].

After the installation you should be able to start minikube with the command `minikube start --driver kvm2` and get access to the cluster with `kubectl get po -A`. The command `minikube dashboard` starts a dashboard, where you can inspect your cluster on a local website. If you like you can start it with this command in the background: `nohup minikube dashboard >/dev/null 2>/dev/null &`, but then it's only possible to stop the dashboard by stopping minikube with `minikube stop`.

You can start one cluster with docker `minikube start --driver=docker -p docker` and a second cluster with `minikube start -p kubevirt --driver=kvm2`. You should now see both profiles running with `minikube profile list`. This may be helpful for testing. [@minikubekubevirt]

Minikube creates a VM with 16GB or 20GB disk space. To prevent later errors in the step "Preparing desktop images with cloud-init" which occur due to insufficient space you should create a minikube instance with the parameter `--disk-size=XXGB`, where `XX` is the amount of space you want to use. You can also increase the memory and CPU amount with `--memory` and `--cpus`. We use `minikube start --vm-driver=kvm2 --memory=8192 --cpus=4 --disk-size=50GB`. In the next steps you should remember to add this parameter by yourself. [@minikubedisksize] [@redhatminikubemem]

Also it's needed to use a network plugin that supports NetworkPolicy. The one we are using is called calico and can be configured during startup with `--cni=calico`. With the parameters from above this results into `minikube start --driver kvm2 --memory=8192 --cpus=4 --disk-size=50g --cni=calico`. [@minikubesetup] [@k8networking]

`kubectl` is now configured to use more than one cluster. There should be two contexts in `kubectl config view`: `docker` and `kubevirt`. You can use the minikube kubectl command like this to specify which cluster you would like to use: `minikube kubectl get pods -p docker` and `minikube kubectl get vms -p kubevirt`. Or you can specify the context in kubectl like this: `kubectl get pods --context docker` and `kubectl get vms --context kubevirt`.

You can stop them with `minikube stop -p docker` and `minikube stop -p kubevirt`. Deleting them works with the commands `minikube delete -p docker` and `minikube delete -p kubevirt`.

It is sufficient to only run one cluster with kvm2 driver, because this can execute docker as well.

### Kubernetes Productive Installation
<!-- TODO -->

### Helm, Krew, KubeVirt and Virtctl Installation
Start minikube: `minikube start --driver kvm2 --memory=8192 --cpus=4 --disk-size=50g --cni=calico`.

Install Helm using [this guide](https://helm.sh/docs/intro/install/)^[https://helm.sh/docs/intro/install/].

Install Krew using [this guide](https://krew.sigs.k8s.io/docs/user-guide/setup/install/)^[https://krew.sigs.k8s.io/docs/user-guide/setup/install/].

If you are running Minikube, use this installation guide to install KubeVirt and then Virtctl with Krew: [KubeVirt quickstart with Minikube](https://kubevirt.io/quickstart_minikube/)^[https://kubevirt.io/quickstart_minikube/]. Verify the installation. This adds some commands to kubectl for example `kubectl get vms` instead of `kubectl get pods`.

Start kubevirt in the minikube cluster: `minikube addons enable kubevirt` or use the in-depth way. After that deploy a test VM using this guide: [Use KubeVirt](https://kubevirt.io/labs/kubernetes/lab1)^[https://kubevirt.io/labs/kubernetes/lab1]

You also need to [install CDI](https://kubevirt.io/user-guide/operations/containerized_data_importer/#install-cdi)^[https://kubevirt.io/user-guide/operations/containerized_data_importer/#install-cdi] which is an extension for KubeVirt.

<!-- TODO: test if kubevirt works with docker -->

## %project_name% Installation
<!-- TODO -->

\vfill
