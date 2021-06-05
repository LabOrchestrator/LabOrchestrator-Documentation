\pagebreak

# Prototype

## KubeVirt and Virtual Machines
You should have installed kubectl and minikube with activated kubevirt addon.

KubeVirt has a tool called Containerized Data Importer (CDI), which is designed to import Virtual Machine images for use with KubeVirt. This needs to be installed from here: [Containerized Data Importer (CDI)](https://kubevirt.io/labs/kubernetes/lab2.html)^[https://kubevirt.io/labs/kubernetes/lab2.html].

The installation of KubeVirt and CDI adds several new CRs, which can be found in the [documentation of kubevirt](https://kubevirt.io/user-guide/)^[https://kubevirt.io/user-guide/].

Resources from Kubernetes:

- PersistentVolume (PV)
    - already included in Kubernetes
- PersistentVolumeClaim (PVC)
    - already included in Kubernetes

CRs from KubeVirt:

- VirtualMachine (VM)
    - An image of an VM, e.g. Fedora 23
    - Can only be started once
- VirtualMachineInstance (VMI)
    - An instance of an VM, e.g. the Lab i'm currently using
- VirtualMachineSnapshot
- VirtualMachineSnapshotContent
- VirtualMachineRestore
- VirtualMachineInstanceMigration
- VirtualMachineInstanceReplicaSet
- VirtualMachineInstancePreset

CRs from CDI:

- StorageProfile
- Containerized Data Importer (CDI)
    - converts an VM image into the correct format to use it as VM in KubeVirt
- CDIConfig
- DataVolume (DV)
- ObjectTransfer

There is an example vm config in the KubeVirt documentation. [@kubevirtlab1] Download the vm config `wget https://raw.githubusercontent.com/kubevirt/kubevirt.github.io/master/labs/manifests/vm.yaml` and apply it: `kubectl apply -f vm.yaml`. Now you should see, that there is a new VM in `kubectl get vms` called testvm. You can start the VM with `kubectl virt start testvm`. This creates a new VM instance (VMI) that you can see in `kubectl get vmis`. You can then connect to the serial console using `kubectl virt console testvm`. Exit the console with `ctrl+]` and stop the VM with `kubectl virt stop testvm`. Stoping the VM deletes all changes made inside the VM and when you start it again, a new instance is created without the changes. You can start a VM only once.

When a VM gets started, its `status.created` attibutes becomes `true`. If the VM instance is ready, `status.ready` becomes `true` too. When the VM gets stopped, the attributes gets removed. A VM will never restart a VMI until the current instance is deleted. [@kubevirtdocarch]

After starting the VM you can expose its ssh port with this command: `kubectl virt expose vm testvm --name vmiservice --port 27017 --target-port 22`. Then you can get the cluster-ip from `kubectl get svc`. The cluster ip can't be used directly to connect with ssh, but from inside minikube. So to connect to the ssh of the VM execute `minikube ssh`. This logs you in to the minikube environment. From there you can execute the corresponding ssh command, e.g. `ssh -p 27017 cirros@10.102.92.133`.


Example VM (`prototype/vm.yaml`):

```{include=prototype/vm.yaml}
```


### KubeVirt UIs
There is a comparison about different KubeVirt User Interfaces: [KubeVirt user interface options](https://kubevirt.io/2019/KubeVirt_UI_options.html)^[https://kubevirt.io/2019/KubeVirt_UI_options.html].


### KubeVirt Additional Plugins
The [local persistence volume static provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner)^[https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner] manages the PersistentVolume lifecycle for preallocated disks.

## Base images

## Web access to terminal

## Web access to graphical user interface
https://kubevirt.io/2019/Access-Virtual-Machines-graphic-console-using-noVNC.html
## Integration of terminal and graphical user interface web access to docker base image

## Integration of terminal and graphical user interface web access to VM base image

## Integration of base images in Kubernetes

## Routing of base images in Kubernetes

## Multi-user support
