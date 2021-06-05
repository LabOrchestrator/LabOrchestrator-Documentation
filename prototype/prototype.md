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

### KubeVirt Basics

There is an example vm config in the KubeVirt documentation. [@kubevirtlab1] Download the vm config `wget https://raw.githubusercontent.com/kubevirt/kubevirt.github.io/master/labs/manifests/vm.yaml` and apply it: `kubectl apply -f vm.yaml`. Now you should see, that there is a new VM in `kubectl get vms` called testvm. You can start the VM with `kubectl virt start testvm`. This creates a new VM instance (VMI) that you can see in `kubectl get vmis`. You can then connect to the serial console using `kubectl virt console testvm`. Exit the console with `ctrl+]` and stop the VM with `kubectl virt stop testvm`. Stoping the VM deletes all changes made inside the VM and when you start it again, a new instance is created without the changes. You can start a VM only once.

When a VM gets started, its `status.created` attibutes becomes `true`. If the VM instance is ready, `status.ready` becomes `true` too. When the VM gets stopped, the attributes gets removed. A VM will never restart a VMI until the current instance is deleted. [@kubevirtdocarch]

After starting the VM you can expose its ssh port with this command: `kubectl virt expose vm testvm --name vmiservice --port 27017 --target-port 22`. Then you can get the cluster-ip from `kubectl get svc`. The cluster ip can't be used directly to connect with ssh, but from inside minikube. So to connect to the ssh of the VM execute `minikube ssh`. This logs you in to the minikube environment. From there you can execute the corresponding ssh command, e.g. `ssh -p 27017 cirros@10.102.92.133`. [@kubevirtdocarch]

VMIs can be paused and unpaused with the commands `kubectl virt pause vm testvm` or `kubectl virt pause vmi testvm` and the commands `kubectl virt unpause vm testvm` or `kubectl virt unpause vmi testvm`. This freezes the process of the VMI, that means that the VMI has no longer access to CPU and I/O but the memory will stay allocated. [@kubevirtdoclife]

Example VM (`prototype/vm.yaml`): [@kubevirtlab1]

```{include=prototype/vm.yaml}
```

### KubeVirt Run Strategies

VirtualMachines have different so called run strategies. If a VMI crashes it restarts if you set `spec.running: true`, but by defining a `spec.RunStrategy` this behaviour can be changed. You can only use `spec.running` or `spec.RunStrategy` and not both at the same time. There are four run strategies: [@kubevirtdocrun]

- Always: If the VMI crashes, a new one is created. It's the same as setting `spec.running: true`
- RerunOnFailure: VMI restarts, if the previous failed in an error state. It will not be re-created if the guest stopped it.
- Manual: It doesn't restart until someone starts it manually.
- Halted: This means, the VMI is stopped. It's the same as setting `spec.running: false`

### KubeVirt Presets

`VirtualMachineInstancePreset` is a resource that can be used to create re-usable settings that can be applied to various machines. These presets work like the `PodPreset` resource from Kubernetes. They are namespaces, so if you need to add these presets to every namespace where you need it. Any domain structure can be added in the `spec` of a preset, for example memory, disks and network interfaces. The presets uses `Labels` and `Selectors` to determine which VMI is affected from the preset. If you don't add any selector, the preset will be applied to all VMIs in the namespace. [@kubevirtdocpreset]

You can use presets to define a set of specs with different values and give them labels and then customise VMIs with them. This abstracts some of the specs of VMIs and make it easily customisable to change the specs of a VMI. [@kubevirtdocpreset]

Example `VirtualMachineInstancePreset`: [@kubevirtdocpreset]

```
apiVersion: kubevirt.io/v1alpha3
kind: VirtualMachineInstancePreset
metadata:
  name: small-qemu
spec:
  selector:
    matchLabels:
      kubevirt.io/size: small
  domain:
    resources:
      requests:
        memory: 64M
```

Example VMI, that matches the correct labels: [@kubevirtdocpreset]

```
apiVersion: kubevirt.io/v1alpha3
kind: VirtualMachineInstance
version: v1
metadata:
  name: myvmi
  labels:
    kubevirt.io/size: small
```

The example shows a preset, which applies 64M of memory to every VMI with the label `kubevirt.io/size: small`. [@kubevirtdocpreset]

When a preset and a VMI define the same specs but with different values there is a collision. Collisions are handled in the way that the VMI settings override the presets settings. If there are collisions between two presets that are applied to the same VMI an error occurs. [@kubevirtdocpreset]

If you change a preset it is only applied to new created VMIs. Old VMIs doesn't change. [@kubevirtdocpreset]

### KubeVirt Disks and Volumes
https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/

### KubeVirt Interfaces and Networks
https://kubevirt.io/user-guide/virtual_machines/interfaces_and_networks/

### KubeVirt Network Policy
Maybe needed to separate userspaces or to connect all users machines.
https://kubevirt.io/user-guide/virtual_machines/networkpolicy/

### KubeVirt Snapshots
KubeVirt has a feature called snapshots. This is currently not documented, but in the near future it may be a good solution for pausing VMs.

### KubeVirt ReplicaSets
https://kubevirt.io/user-guide/virtual_machines/replicaset/

### KubeVirt Running Windows
https://kubevirt.io/user-guide/virtual_machines/windows_virtio_drivers/

### KubeVirt Services

### KubeVirt Other Features

There are several other features that we are not going into detail but recommend reading. The most interesting features are the following:
- [Virtual Hardware](https://kubevirt.io/user-guide/virtual_machines/virtual_hardware/)^[https://kubevirt.io/user-guide/virtual_machines/virtual_hardware/], e.g. Resources like CPU, timezone, GPU and memory.
- [Liveness and Readiness Probes](https://kubevirt.io/user-guide/virtual_machines/liveness_and_readiness_probes/)^[https://kubevirt.io/user-guide/virtual_machines/liveness_and_readiness_probes/]
- [Startup Scripts](https://kubevirt.io/user-guide/virtual_machines/startup_scripts/)^[https://kubevirt.io/user-guide/virtual_machines/startup_scripts/]

### KubeVirt CDI
https://kubevirt.io/user-guide/operations/containerized_data_importer/

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

### Authorization
[KubeVirt Authorization](https://kubevirt.io/user-guide/operations/authorization/)^[https://kubevirt.io/user-guide/operations/authorization/]
