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

To run %project_name% you need an instance of Kubernetes with KubeVirt.

For development we use minikube. To install minikube install docker and [kvm2](https://minikube.sigs.k8s.io/docs/drivers/kvm2/)^[https://minikube.sigs.k8s.io/docs/drivers/kvm2/] or some other driver for VMs and follow [this guide](https://minikube.sigs.k8s.io/docs/start/)^[https://minikube.sigs.k8s.io/docs/start/]. Also install `kubectl` using [this guide](https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/)^[https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/].

After the installation you should be able to start minikube with the command `minikube start --driver kvm2` and get access to the cluster with `kubectl get po -A`. The command `minikube dashboard` starts a dashboard, where you can inspect your cluster on a local website. If you like you can start it with this command in the background: `nohup minikube dashboard >/dev/null 2>/dev/null &`, but then it's only possible to stop the dashboard by stopping minikube with `minikube stop`.

You can start one cluster with docker `minikube start --driver=docker -p docker` and a second cluster with `minikube start -p kubevirt --driver=kvm2`. You should now see both profiles running with `minikube profile list`. This may be helpful for testing. [@minikubekubevirt]

Minikube creates a VM with 16GB or 20GB disk space. To prevent later errors in the step "Preparing desktop images with cloud-init" which occur due to insufficient space you should create a minikube instance with the parameter `--disk-size=XXGB`, where `XX` is the amount of space you want to use. You can also increase the memory and CPU amount with `--memory` and `--cpus`. We use `minikube start --vm-driver=kvm2 --memory=8192 --cpus=4 --disk-size=50GB`. In the next steps you should remember to add this parameter by yourself. [@minikubedisksize] [@redhatminikubemem]

Also it's needed to use a network plugin that supports NetworkPolicy. The one we are using is called calico and can be configured during startup with `--cni=calico`. With the parameters from above this results into `minikube start --driver kvm2 --memory=8192 --cpus=4 --disk-size=50g --cni=calico`. [@minikubesetup] [@k8networking]

`kubectl` is now configured to use more than one cluster. There should be two contexts in `kubectl config view`: `docker` and `kubevirt`. You can use the minikube kubectl command like this to specify which cluster you would like to use: `minikube kubectl get pods -p docker` and `minikube kubectl get vms -p kubevirt`. Or you can specify the context in kubectl like this: `kubectl get pods --context docker` and `kubectl get vms --context kubevirt`.

You can stop them with `minikube stop -p docker` and `minikube stop -p kubevirt`. Deleting them works with the commands `minikube delete -p docker` and `minikube delete -p kubevirt`.

It is sufficient to only run one cluster with kvm2 driver, because this can execute docker as well.

### Kubernetes Productive Installation

To run %project_name% you need an instance of Kubernetes with KubeVirt. In our production environment we use minikube too, but you can also use Kind. I've used the same installation as in production so take a look there.

Currently I'm running minikube with docker driver. Probably this isn't the best way of running Kubernetes, but it's working. To add SSL I've added traefik to docker:

~~~{#lst:dctraefik .yaml .long .numberLines caption="traefik/docker_compose.yml"}
version: '3'

services:
  reverse-proxy:
    image: traefik:v2.2
    restart: unless-stopped
    command:
      - --api=true
      - --api.insecure=false
      - --api.dashboard=true
      - --accesslog=true
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.myresolver.acme.tlschallenge=true
      - --certificatesresolvers.myresolver.acme.email=YOUR@MAIL.COM
      - --certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json
    labels:
      - "co.elastic.logs/module=traefik"
      - "traefik.enable=true"
      - "traefik.http.routers.traefik-api.rule=Host(`YOUR.DOMAIN.COM`)"
      - "traefik.http.routers.traefik-api.entrypoints=websecure"
      - "traefik.http.routers.traefik-api.tls.certresolver=myresolver"
      - "traefik.http.routers.traefik-api.service=api@internal"
      - "traefik.http.routers.traefik-api.middlewares=auth"
      - "traefik.http.middlewares.auth.basicauth.users=user:password
      - "traefik.http.services.traefik-api.loadbalancer.server.port=8080"
      - "traefik.http.routers.http-catchall.rule=hostregexp(`{host:.+}`)"
      - "traefik.http.routers.http-catchall.entrypoints=web"
      - "traefik.http.routers.http-catchall.middlewares=redirect-to-https@docker"
      - "traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https"
      - "traefik.http.middlewares.redirect-to-https.redirectscheme.permanent=true"
      - "traefik.docker.network=traefik_default"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "/letsencrypt:/letsencrypt"
~~~

After this you need to add a reverse proxy that adds routing to our Kubernetes cluster. This is done with a docker container that runs nginx. These two files are needed for this:

~~~{#lst:kubeproxy .yaml .long .numberLines caption="kubeproxy/dockerfile"}
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
~~~

~~~{#lst:kubeproxy .long .numberLines caption="kubeproxy/nginx.conf"}
server {
    listen 8010 default_server;
    listen [::]:8010 default_server;

    server_name _;

    location / {
        proxy_pass http://MINIKUBEIP:30001;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
    location /labvnc/ {
        proxy_pass http://MINIKUBEIP:30003/;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }
    location /ws_proxy/ {
        proxy_pass http://MINIKUBEIP:30002;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
~~~

After starting these containers and opening the domain traefik will get an SSL certificate and the connections are secured.

### Helm, Krew, KubeVirt and Virtctl Installation
Start minikube: `minikube start --driver kvm2 --memory=8192 --cpus=4 --disk-size=50g --cni=calico`.

Install Helm using [this guide](https://helm.sh/docs/intro/install/)^[https://helm.sh/docs/intro/install/].

Install Krew using [this guide](https://krew.sigs.k8s.io/docs/user-guide/setup/install/)^[https://krew.sigs.k8s.io/docs/user-guide/setup/install/].

If you are running Minikube, use this installation guide to install KubeVirt and then Virtctl with Krew: [KubeVirt quickstart with Minikube](https://kubevirt.io/quickstart_minikube/)^[https://kubevirt.io/quickstart_minikube/]. Verify the installation. This adds some commands to kubectl for example `kubectl get vms` instead of `kubectl get pods`.

Start kubevirt in the minikube cluster: `minikube addons enable kubevirt` or use the in-depth way. After that deploy a test VM using this guide: [Use KubeVirt](https://kubevirt.io/labs/kubernetes/lab1)^[https://kubevirt.io/labs/kubernetes/lab1]

You also need to [install CDI](https://kubevirt.io/user-guide/operations/containerized_data_importer/#install-cdi)^[https://kubevirt.io/user-guide/operations/containerized_data_importer/#install-cdi] which is an extension for KubeVirt.

## %project_name% Production Installation

First install the prerequisites for production.

To install %project_name% you need to get the yaml files from [github.com/LabOrchestrator/LabOrchestrator/kubernetes](https://github.com/LabOrchestrator/LabOrchestrator/tree/main/kubernetes)^[https://github.com/LabOrchestrator/LabOrchestrator/tree/main/kubernetes]. First **change the config** in these files:

- `websocket_proxy/websocket_proxy.yaml`:
    - Replace the secret key.
    - Add your host path prefix that is used in the nginx proxy.
- `postgres/config_map.yaml`:
    - Replace the username and password.
- `lab_orchestrator_api/lab_config.yaml`:
    - Replace django config, mail config and secret key with corresponding values.
    - Replace allowed hosts with your domain name.
    - Replace `LAB_VNC_HOST` and `WS_PROXY_HOST` with the ip of minikube.
    - Replace the prefix in the lab vnc path with the prefix used in nginx.
    - Replace the lab vnc protocol with https.

After that run `make build`. This generates a new `lab_orchestrator.yaml`. This file can than be used to deploy the application with `kubectl apply -f lab_orchestrator.yaml` or `make deploy`.

When you make changes to the config in the API you can restart it with `make restart-api`.

If you remove the deployment the postgres DB may be deleted, so create backups from time to time.

### Adding VMs

In the next chapters you can see how to create VMs, in short just create a VM with gnome boxes and then use the produced qcow2 image that is located in `~/.var/app/org.gnome.Boxes/data/gnome-boxes/images/` or in `~/.local/share/gnome-boxes`.

This file needs to be added into a docker image and uploaded to docker hub. This is done with the following dockerfile:

~~~{#lst:createvminsta .yaml .long .numberLines caption="dockerfile to add VMs"}
FROM scratch
ADD --chown=107:107 YOURIMAGE.qcow2 /disk/
~~~

Build it with `docker build -t username/repo:version` and push it with `docker push username/repo:version`.

Then add a new docker file to the lab orchestrator api that URL is `username/repo:version`.

### Updating VMs

From time to time you need to update the VM images. For this just open them in gnome boxes again, perform updates and stop the VM. Then build a new docker image with the new qcow2 image and push it to docker hub with an increased version.

After that update the URL from the docker image in lab orchestrator with the new version. All newly created instances that uses this docker image will now have use the new version.


\vfill
