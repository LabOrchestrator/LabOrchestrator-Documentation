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


~~~{#lst:mypython .yaml .numberLines caption="Example VM (prototype/vm.yaml)" include=prototype/vm.yaml}
~~~

The source of the example can be found in [@kubevirtlab1].

### KubeVirt Run Strategies

VirtualMachines have different so called run strategies. If a VMI crashes it restarts if you set `spec.running: true`, but by defining a `spec.RunStrategy` this behaviour can be changed. You can only use `spec.running` or `spec.RunStrategy` and not both at the same time. There are four run strategies: [@kubevirtdocrun]

- Always: If the VMI crashes, a new one is created. It's the same as setting `spec.running: true`
- RerunOnFailure: VMI restarts, if the previous failed in an error state. It will not be re-created if the guest stopped it.
- Manual: It doesn't restart until someone starts it manually.
- Halted: This means, the VMI is stopped. It's the same as setting `spec.running: false`

### KubeVirt Presets

`VirtualMachineInstancePreset` is a resource that can be used to create re-usable settings that can be applied to various machines. These presets work like the `PodPreset` resource from Kubernetes. They are namespaces, so if you need to add these presets to every namespace where you need it. Any domain structure can be added in the `spec` of a preset, for example memory, disks and network interfaces. The presets uses `Labels` and `Selectors` to determine which VMI is affected from the preset. If you don't add any selector, the preset will be applied to all VMIs in the namespace. [@kubevirtdocpreset]

You can use presets to define a set of specs with different values and give them labels and then customise VMIs with them. This abstracts some of the specs of VMIs and make it easily customisable to change the specs of a VMI. [@kubevirtdocpreset]

~~~{#lst:exmplvmipreset .yaml .numberLines caption="Example VirtualMachineInstancePreset"}
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
~~~


~~~{#lst:exmplvmilabel .yaml .numberLines caption="Example VMI, that matches the correct labels"}
apiVersion: kubevirt.io/v1alpha3
kind: VirtualMachineInstance
version: v1
metadata:
  name: myvmi
  labels:
    kubevirt.io/size: small
~~~

The source of the examples can be found in [@kubevirtdocpreset]. The example shows a preset, which applies 64M of memory to every VMI with the label `kubevirt.io/size: small`. [@kubevirtdocpreset]

When a preset and a VMI define the same specs but with different values there is a collision. Collisions are handled in the way that the VMI settings override the presets settings. If there are collisions between two presets that are applied to the same VMI an error occurs. [@kubevirtdocpreset]

If you change a preset it is only applied to new created VMIs. Old VMIs doesn't change. [@kubevirtdocpreset]

### KubeVirt Disks and Volumes

#### Disks
Disks are like virtual disks to the VM. They can for example be mounted from inside /dev. Disks are specified in `spec.domain.devices.disks` and need to reference the name of a volume. [@kubevirtdocdisks]

Possible disk types are: `lun`, `disk` and `cdrom`. `disk` is an ordinary disk to the VM. `lun` is a disk that uses iCSI commands. And `cdrom` is exposed as a cdrom drive and read-only by default. [@kubevirtdocdisks]

Disks have a bus type. A bus type indicates the type of disk device to emulate. Possible types are: `virtio`, `sata`, `scsi`, `ide`. [@kubevirtapi]

#### Volumes
Volumes are a Kubernetes Concept. They try to solve the problem of ephemeral disks. Without volumes, if a container restarts, it restarts with a clean state and it's not possible to save any state. Volumes allows to have a disk attached, that is persistent. There are ephemeral and persistent volumes. Ephemeral volumes have the same lifetime as a pod. Persistent volumes aren't deleted. For both of them in a given pod, data is preserved across container restarts. [@k8docsvolumes]

In the context of KubeVirt, volumes define the KubeVirts type of the disk. For example you can make them persistent in your cluster or even store them in a container image registry. [@kubevirtdocdisks]

Possible disk types are: `cloudInitNoCloud`, `cloudInitConfigDrive`, `persistentVolumeClaim`, `persistentVolumeClaim`, `dataVolume`, `ephemeral`, `containerDisk`, `emptyDisk`, `hostDisk`, `configMap`, `secret`, `serviceAccount`, `downwardMetrics`. [@kubevirtdocdisks]

#### cloudInitNoCloud
`cloudInitNoCloud` can be used to attach some user-data to the VM, if the VM contains a proper cloud-init setup. The NoCloud data will be added as a disk to the VMI. This can be used for example to automatically put an ssh key into `~/.ssh/authorized_keys`. For more information see the [cloudinit nocloud documentation](http://cloudinit.readthedocs.io/en/latest/topics/datasources/nocloud.html)^[http://cloudinit.readthedocs.io/en/latest/topics/datasources/nocloud.html] or the [KubeVirt cloudInitNoCloud documentation](https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/#cloudinitnocloud)^[https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/#cloudinitnocloud]. [@kubevirtdocdisks]

#### Persistent Volumes and Persistent Volume Claims
Kubernetes provides some resources for providing persistent storage. The first is a `PersistentVolume`. A `PersistentVolume` is a piece of storage in the cluster that is reserved from a cluster administrator or it is dynamically provisioned using Storage Classes. [@k8docsstorageclass] A `StorageClass` is the second resource and it is a way for administrators to customize the types of storage the offer. [@k8docspv] You can read more about `StorageClass` and `PersistentVolume` in the Kubernetes documentation about [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/#local)^[https://kubernetes.io/docs/concepts/storage/storage-classes/#local] and [PersistentVolumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)^[https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims].

A `PersistentVolumeClaim` (PVC) is the third resource provided by Kubernetes. It is a request for storage by a user. In KubeVirt it is used, when the VMIs disk needs to persist after the VM terminates. This makes the VM data persistent between restarts. `PersistentVolumes` and `StorageClasses` can be used to customize the Storage that can be provided to PVCs. [@kubevirtdocdisks]


~~~{#lst:exmplvmipvc .yaml .numberLines caption="Example of VMI with PVC"}
metadata:
  name: testvmi-pvc
apiVersion: kubevirt.io/v1alpha3
kind: VirtualMachineInstance
spec:
  domain:
    resources:
      requests:
        memory: 64M
    devices:
      disks:
      - name: mypvcdisk
        lun: {}
  volumes:
    - name: mypvcdisk
      persistentVolumeClaim:
        claimName: mypvc
~~~

The source of the example can be found in [@kubevirtdocdisks]. This examples creates a VMI and attaches a PVC with the name `mypvc` as a lun disk.

#### Data Volumes
`dataVolume` are part of the Containerized Data Importer (CDI) which need to be installed separately. A data volume is used to automate importing VM disks onto PVCs. Without a `DataVolume`, users have to prepare a PVC with a disk image before assigning it to a VM. DataVolumes are defined in the VM spec by adding the attribute list `dataVolumeTemplates`. The specs of a data volume contain a `source` and `pvc` attribute. `source` describes where to find the disk image. `pvc` describes which specs the PVC that is created should have. An example can be found [here](https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/#datavolume-vm-behavior)^[https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/#datavolume-vm-behavior]. When the VM is deleted, the PVC ist deleted as well. When a VM manifest is posted to the cluster (for example with a yaml config), the PVC is created directly before the VM is even started. That may be used for performance improvements when starting a VM. It is possible to attach a data volume while creating a VMI, but then the data volume is not tied to the life-cycle of the VMI. [@kubevirtdocdisks]

#### Container Disks
`containerDisk` is a volume that references a docker image. The disks are pulled from the container registry and reside on the local node. It is an ephemeral storage device and can be used by multiple VMIs. This makes them an ideal tool for users who want to replicate a large number of VMs that do not require persistent data. They are often used in `VirtualMachineInstanceReplicaSet`. They are not a good solution if you need persistent root disks across VM restarts. Container disks are file based and therefore cannot be attached as a lun device. [@kubevirtdocdisks]

To use container disks you need to create a docker image which contains the VMI disk. The disk must be placed into the `/disk` directory of the container and must be readable for the user with the UID 107 (qemu). The format of the VMI disk must be raw or qcow2. The base image of the docker image should be based on the docker `scratch` base image and no other content except the image is required. [@kubevirtdocdisks]

~~~{#lst:exmpldocker1 .dockerfile .numberLines caption="Dockerfile example with local qcow2 image"}
FROM scratch
ADD --chown=107:107 fedora25.qcow2 /disk/
~~~

~~~{#lst:exmpldocker2 .dockerfile .numberLines caption="Dockerfile example with remote qcow2 image"}
FROM scratch
ADD --chown=107:107 https://cloud.centos.org/centos/7/images/CentOS-7-x86_64-GenericCloud.qcow2 /disk/
~~~

~~~{#lst:exmplcontainerdisk .dockerfile .numberLines caption="Example VMI with Container Disk"}
metadata:
  name: testvmi-containerdisk
apiVersion: kubevirt.io/v1alpha3
kind: VirtualMachineInstance
spec:
  domain:
    resources:
      requests:
        memory: 8G
    devices:
      disks:
      - name: containerdisk
        disk: {}
  volumes:
    - name: containerdisk
      containerDisk:
        image: vmidisks/fedora25:latest
~~~

The source of the examples can be found in [@kubevirtdocdisks]. The dockerfiles can then be build with `docker build -t example/example:latest .` and pushed to a remote docker container registry with `docker push example/example:latest`. [@kubevirtdocdisks]

#### Empty Disks and Ephemeral Disks
`emptyDisk` is a temporary disk which shares the VMIs lifecycle. The disk lifes as long as the VM, so it will persist between reboots and will be deleted when the VM is deleted. You need to specify the `capacity`. [@kubevirtdocdisks]

`ephemeral` is also a temporary disk, but it wraps around `PersistentVolumeClaims`. It is mounted as read-only network volume. An ephemeral volume is never mutated, instead all writes are stored on the ephemeral image which exists locally. The local image is created when a VM starts and it is deleted when the VM stops. They are useful when persistence is not needed. [@kubevirtdocdisks]

The difference between `ephemeral` and `emptyDisk` is, that `ephemeral` disks are read only and there is only a small space for application data. Also the application data is deleted, when the VM reboots. This can cause problem to some applications and then it's useful to use `emptyDisks`. [@kubevirtdocdisks]

#### Remaining Volumes
`hostDisk`, `configMap`, `secrets` and the other volumes are explained in the [KubeVirt Disks and Volumes Documentation](https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/)^[https://kubevirt.io/user-guide/virtual_machines/disks_and_volumes/].

### KubeVirt Interfaces and Networks
There are two parts needed to connect a VM to a network. First there is the interface that is a virtual network interface of a virtual machine and second there is the network which connects VMs to logical or physical devices.

Networks need unique names and a type. There are two fields in a network. The first field is `pod`. A pod network is the default `eth0` interface. [@kubevirtdocinterfaces] And the second field is Multus. Multus enables attaching a secondary interface that enables multiple network interfaces in Kubernetes. To be able to use multus it needs to be installed separately. [@multusgit]

Interfaces describe the properties of a virtual interface and are seen inside the quest instance. They are defined in `spec.domain.devices.interfaces`. You can specify its type by adding the type with curly brackets (`masquerade: {}`). Available types are `bridge`, `slirp`, `sriov` and `masquerade`. Other properties that you can change are `model`, `macAddress`, `ports` and `pciAddress`. Custom mac addresses are not always supported.

You can read more about the types [here](https://kubevirt.io/user-guide/virtual_machines/interfaces_and_networks/)^[https://kubevirt.io/user-guide/virtual_machines/interfaces_and_networks/]

~~~{#lst:exmplnet .yaml .numberLines caption="Example Network and Interface"}
kind: VM
spec:
  domain:
    devices:
      interfaces:
        - name: default
          masquerade: {}
          ports:
           - name: http
             port: 80
  networks:
  - name: default
    pod: {}
~~~

The ports field can be used to limit the ports the VM listens to.

If you would like to disable network connectivity, you can use the `autoattachPodInterface` field.

~~~{#lst:exmplaapi .yaml .numberLines caption="Example of autoattachPodInterface"}
kind: VM
spec:
  domain:
    devices:
      autoattachPodInterface: false
~~~

### KubeVirt Network Policy

By default, all VMIs in a namespace share a network and are accessible from other VMIs. To isolate them, you can create NetworkPolicy objects. NetworkPolicy objects entirely control the network isolation in a namespace. Examples on how to deny all traffic, only allow traffic in the same namespace or only allow HTTP and HTTPS access can be found [here](https://kubevirt.io/user-guide/virtual_machines/networkpolicy/)^[https://kubevirt.io/user-guide/virtual_machines/networkpolicy/]. [@kubevirtnet]

NetworkPolicy objects are included in Kubernetes and are used to separate networks of pods. But with KubeVirt installed, VMIs and pods are treated equally and NetworkPolicy objects can be used for VMIs too. We need to add NetworkPolicy objects to isolate the VMIs of different users, so that the users can't connect to the VMIs of other users. If we create a new namespace for every user, the default settings are sufficient, but creating NetworkPolicy objects gives us more flexibility, e.g. cross namespace connections or isolation of ports. [@k8net]

**To use network policies you need to install a network plugin, that supports network policies. So make sure your cluster fulfills this condition.** [@k8net]

Network policies are additive, so if you add two policies the union of them is chosen. If the egress policy or the ingress policy on a pod denies the traffic, the traffic will not be possible even though the network policy would allow it. [@k8net]

How to create and use a NetworkPolicy object is described in the [kubernetes network policy documentation](https://kubernetes.io/docs/concepts/services-networking/network-policies/#networkpolicy-resource)^[https://kubernetes.io/docs/concepts/services-networking/network-policies/#networkpolicy-resource]. You need to define a name of the network policy in the `metadata.name` field and you can specify the namespace this network policy is running in in the `metadata.namespace` field. After that you can specify the policy in the `spec` field. The `spec` field contains a `podSelector`, `policyTypes`, `ingress` and `egress` fields. The `podSelector` field selects the pods the policy will be applied to by defining labels. If the selector is empty all pods in the namespace are selected. Available `policyTypes` are `Ingress` and `Egress`. They can be added to this field to include them. The `Ingress` type is used for incoming requests and the `Egress` type is used for outgoing requests. If you don't specify this field, `Ingress` is activated by default and `Egress` only if an `Egress` rule is added. To add `Ingress` and `Egress` rules there is also the `ingress` and `egress` field in `spec`. Each `ingress` rule allows traffic which matches both the `from` and `ports` sections. The `egress` rules matches both the `to` and `ports` sections. Inside the `from` or `to` sections you can specify for example a `podSelector`, an `ipBlock` or a `namespaceSelector`. The full list of available options can be found in the [NetworkPolicy reference](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.21/#networkpolicy-v1-networking-k8s-io)^[https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.21/#networkpolicy-v1-networking-k8s-io]. [@k8net]

~~~{#lst:policyexmpl .yaml .numberLines caption="Example of NetworkPolicy"}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: multi-port-egress
  namespace: default
spec:
  podSelector:
    matchLabels:
      role: db
  policyTypes:
  - Egress
  egress:
  - to:
    - ipBlock:
        cidr: 10.0.0.0/24
    ports:
    - protocol: TCP
      port: 32000
      endPort: 32768
~~~

The example shows a network policy with an `Egress` rule that allows all pods and VMIs with the label `role: db` to connect to all pods and VMIs within the IP range 10.0.0.0/24 over TCP with the ports between 32000 and 32778. The source of the example can be found here: [@k8net].

### KubeVirt ReplicaSets
`VirtualMachineInstanceReplicaSet`s are similar like Kubernetes `ReplicaSets`. They are used to deploy multiple instances of the same VMI to guarantee uptime. There is no state in the instances of a `ReplicaSet` so you need to use read-only or internal writable tmpfs disks. Since our labs need a state we probably won't need `ReplicaSets`. [@kubevirtreplicas]

### KubeVirt Services
VMIs can be exposed with services. Services were explained [earlier](#services). This is needed to connect to a VMI for example over SSH. Services use labels to identify the VMI, so you need to add labels to the VMI you want to connect to. To create a new Service you can either create a File and load it with `kubectl -f file.yaml` or you can use the `virtctl` tool (remember it may also be used with `kubectl virt`): `virtctl expose virtualmachineinstance vmi-ephemeral --name lbsvc --type LoadBalancer --port 27017 --target-port 3389`. This command uses the type `LoadBalancer`, other types are `NodePort` and `ClusterIP`. [@kubevirtservices]

~~~{#lst:kubevirtservicevmi .yaml .long .numberLines caption="Example VMI with Labels"}
apiVersion: kubevirt.io/v1alpha3
kind: VirtualMachineInstance
metadata:
  name: vmi-ephemeral
  labels:
    special: key
spec:
  ...
~~~

~~~{#lst:kubevirtservicevmi .yaml .long .numberLines caption="Example VMI exposed as Service"}
apiVersion: v1
kind: Service
metadata:
  name: vmiservice
spec:
  ports:
  - port: 27017
    protocol: TCP
    targetPort: 22
  selector:
    special: key
  type: ClusterIP
~~~

The examples are from [KubeVirts Service Objects Documentation](https://kubevirt.io/user-guide/virtual_machines/service_objects/)^[https://kubevirt.io/user-guide/virtual_machines/service_objects/] and they show a VMI with a Label and a Service that exposes SSH on this VMI.

### KubeVirt Other Features

There are several other features that we are not going into detail but recommend reading. The most interesting features are the following:

- [Virtual Hardware](https://kubevirt.io/user-guide/virtual_machines/virtual_hardware/)^[https://kubevirt.io/user-guide/virtual_machines/virtual_hardware/], e.g. Resources like CPU, timezone, GPU and memory.
- [Liveness and Readiness Probes](https://kubevirt.io/user-guide/virtual_machines/liveness_and_readiness_probes/)^[https://kubevirt.io/user-guide/virtual_machines/liveness_and_readiness_probes/]
- [Startup Scripts](https://kubevirt.io/user-guide/virtual_machines/startup_scripts/)^[https://kubevirt.io/user-guide/virtual_machines/startup_scripts/]
- [KubeVirt Snapshots](https://docs.openshift.com/container-platform/4.6/virt/virtual_machines/virtual_disks/virt-managing-offline-vm-snapshots.html), may be used to pause VMs.
- [KubeVirt user interface options](https://kubevirt.io/2019/KubeVirt_UI_options.html)^[https://kubevirt.io/2019/KubeVirt_UI_options.html], there are different KubeVirt User Interfaces.

### KubeVirt Containerized Data Importer (CDI)
The CDI is a separate project that can be added to KubeVirt. To use this you need to [install it](https://kubevirt.io/user-guide/operations/containerized_data_importer/#install-cdi)^[https://kubevirt.io/user-guide/operations/containerized_data_importer/#install-cdi].

TODO

https://kubevirt.io/user-guide/operations/containerized_data_importer/

### KubeVirt Additional Plugins
The [local persistence volume static provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner)^[https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner] manages the PersistentVolume lifecycle for preallocated disks.

### cloud-init
Cloud-init is a standard for cloud instance initialization. Cloud-init will read any provided metadata and initialize the system accordingly. This includes setting up network and storage devices and configuring SSH. For example it is possible to provide an ssh key as metadata. [@cloudinit]

Cloud-init supports Windows and all major Linux distributions like: Arch, Alpine, Debian, Fedora, RHEL and SLES. [@cloudinitavail]

Cloud-init needs to be integrated into the boot of the VM. For example this can be done with systemd. [@cloudinitboot] In addition cloud-init needs a datasource. There are many supported datasources for different cloud providers, but the most important for this project will be the NoCloud datasource, because this can be used in KubeVirt as we have already seen above. [@cloudinitdatasource] NoCloud allows to provide meta-data to the VM via files on a mounted filesystem. [@cloudinitnocloud]

It is modularized and there are many modules available to support many different system configurations and different tools. The most important will be the SSH module and maybe Apt Configure, Disk Setup and Mount. All modules can be found in the [cloud-init Modules Documentation](https://cloudinit.readthedocs.io/en/latest/topics/modules.html)^[https://cloudinit.readthedocs.io/en/latest/topics/modules.html] and examples can be found in the [cloud-init config examples documentaion](https://cloudinit.readthedocs.io/en/latest/topics/examples.html)^[https://cloudinit.readthedocs.io/en/latest/topics/examples.html].

~~~{#lst:nocloudexmpl .yaml .long .numberLines caption="Example VM with cloud-init NoCloud"}
apiVersion: kubevirt.io/v1alpha1
kind: VirtualMachine
metadata:
  name: myvm
spec:
  terminationGracePeriodSeconds: 5
  domain:
    resources:
      requests:
        memory: 64M
    devices:
      disks:
      - name: registrydisk
        volumeName: registryvolume
        disk:
          bus: virtio
      - name: cloudinitdisk
        volumeName: cloudinitvolume
        disk:
          bus: virtio
  volumes:
    - name: registryvolume
      registryDisk:
        image: kubevirt/cirros-registry-disk-demo:devel
    - name: cloudinitvolume
      cloudInitNoCloud:
        userData: |
          ssh-authorized-keys:
            - ssh-rsa AAAAB3NzaK8L93bWxnyp test@test.com
~~~

This is an example that shows how cloud-init NoCloud could be used in KubeVirt to add an ssh key. The created VM contains two disks, one for the image that should be used and another disk that is used by cloud-init. The source can be found here: [@k8kubevirt].

### KubeVirt Running Windows
https://kubevirt.io/user-guide/virtual_machines/windows_virtio_drivers/

## Building a custom VM
In the first step we try to get a cloud image from a Linux distribution running inside of KubeVirt and then excess it. The second step tries to build a custom image on top of the cloud image. This is needed to install software for labs. In the third and fourth step we will install ttyd and NoVNC or alternatives of that and access them with a web browser.

### Custom Base Image with Cloud-init Setup
In KubeVirt you need cloud-images in the format of `qcow2` or `raw`. You can obtain your preferred distro from [the openstack image guide](https://docs.openstack.org/image-guide/obtain-images.html)^[https://docs.openstack.org/image-guide/obtain-images.html]. The list in the openstack image guide contains images that comes with cloud-init preinstalled. This is useful, because most of them doesn't have a default login and we need to add the login data with cloud-init. In this example we have used the [Ubuntu Hirsute cloud-image](https://cloud-images.ubuntu.com/releases/hirsute/release/)^[https://cloud-images.ubuntu.com/releases/hirsute/release/], saved it in the folder `images` and we have a docker hub account.

~~~{#lst:exmpldockerfilecustomimage .dockerfile .long .numberLines caption="Example Dockerfile for Custom Image"}
FROM scratch
ADD --chown=107:107 images/ubuntu-21.04-server-cloudimg-amd64.img /disk/
~~~

After downloading the image create a dockerfile that adds the image into `/disk/.` The [listing 16](#lst:exmpldockerfilecustomimage) shows how to do this with the ubuntu image. Save this file in a file called `dockerfile`.

After that, build the dockerfile with `docker build -t dockerhubusername/reponame:ubuntu2104 -f dockerfile .`. Then login the docker client to docker hub with `docker login` and providing your login credentials. Then upload the build image to docker hub with `docker push dockerhubusername/reponame:ubuntu2104`. Now you have a docker image in docker hub that contains the ubuntu cloud-image in `/disk/`.

In the next step we will use this image with a container disk to run the ubuntu cloud-image. First create a file called `ubuntu_container_disk.yaml` and add a container disk setup.

~~~{#lst:exmplcontainerdiskcustomimage .yaml .long .numberLines caption="Example Container Disk for Custom Image"}
metadata:
  name: testvmi-containerdisk
  labels:
    special: key
apiVersion: kubevirt.io/v1alpha3
kind: VirtualMachineInstance
spec:
  domain:
    resources:
      requests:
        memory: 500M
    devices:
      disks:
      - name: containerdisk
        disk: {}
      - name: cloudinitdisk
        disk:
          bus: virtio
  volumes:
    - name: containerdisk
      containerDisk:
        image: dockerhubusername/reponame:ubuntu2104
    - name: cloudinitdisk
      cloudInitNoCloud:
        userData: |-
          #cloud-config
          users:
            - name: root
              ssh-authorized-keys:
                - ssh-rsa AAAABSSHKEY
          ssh_pwauth: True
          password: toor
          chpasswd:
            expire: False
            list: |-
               root:toor
~~~

The [listing 17](#lst:exmplcontainerdiskcustomimage) is an example of a container disk that uses the docker image we have created previously. Also there is a cloud-init NoCloud disk attached that adds login credentials that can be used to login to the VM via console and via ssh. In this example the username is root and the password toor. If you want to use ssh replace `ssh-rsa AAAABSSHKEY` with your ssh-key, else remove this part of the configuration. To disable password login set `ssh_pwauth: False`.

Then run this VMI with the command `kubectl apply -f ubuntu_container_disk.yaml` and wait until the VMI is started with `kubectl wait --for=condition=Ready vmis/testvmi-containerdisk` or `kubectl wait --for=condition=Ready -f ubuntu_container_disk.yaml`.

Now the VMI is running and you can access it over console: `kubectl virt console testvmi-containerdisk`. To access the ssh, you need to create a service and connect over `minikube ssh`. Create the service with `kubectl virt expose vmi testvmi-containerdisk --name vmiservice --port 27017 --target-port 22`. You can get the ip with `kubectl get svc`. To connect to ssh, you need to execute `minikube ssh`, then insert you ssh private key with:

~~~{#lst:insertsshkey .bash .long .numberLines caption="Insert SSH Key in Minikube"}
cat <<<EOF > ~/.ssh/id_rsa
YOURSSHKEY
EOF
~~~

After that change the permissions of the file to 600 with `chmod 600 ~/.ssh/id_rsa` and connect to the ip from the service on the given port with `ssh -p PORT root@IP` and you should be connected to the VMI.

![Example of Console Login](./prototype/console.png){ width=95% }

![Example of SSH](./prototype/setup.png){ width=95% }

![Example of SSH Setup Login](./prototype/ssh.png){ width=95% }


### Custom Image

### Web Terminal Access

### Web VNC Access


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
