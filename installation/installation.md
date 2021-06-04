\pagebreak


# Installation

## Prerequisites

### Kubernetes Development Installation

To run %project_name% you need an instance of Kubernetes. If you want to use VMs instead of containers you additionally need to install KubeVirt.

For development we use minikube. To install minikube install docker or some other driver and follow [this guide](https://minikube.sigs.k8s.io/docs/start/)^[https://minikube.sigs.k8s.io/docs/start/]. There are multiple options for the driver and we use the Docker driver.

After the installation you should be able to start minikube with the command `minikube start` and get access to the cluster with `kubectl get po -A`. The command `minikube dashboard` starts a dashboard, where you can inspect your cluster on a local website. If you like you can start it with this command in the background: `nohup minikube dashboard >/dev/null 2>/dev/null &`, but then it's only possible to stop the dashboard by stopping minikube with `minikube stop`.

### Kubernetes Productive Installation

### KubeVirt Installation


## %project_name% Installation
To install the program, execute make install.
