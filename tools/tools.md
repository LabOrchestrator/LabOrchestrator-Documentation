\pagebreak

# Tools
The %project_name% application uses different tools that may be explained before the installation of the application. This chapter will give you an introduction into the tools that are used and required in this project, as well as an explanation about Kubernetes that is needed to understand how the %project_name% application is working on the inside.


## Make
Make is used to resolve dependencies during a build process. In this project make is used to have some shortcuts for complex build commands. For example there is a make command to generate the documentation: `make docs`.

## Generating The Documentation
<!-- TODO: This should be added to the readme aswell -->
The documentation is written in markdown and converted to a pdf using pandoc. To generate the documentation pandoc and latex are used. Install `pandoc`, `pandoc-citeproc` and a latex environment. [@markdownandpandoc]

For the replacement of variables there is a lua script installed, so you need to install lua too. [@luavariablescript]

There is a make command to generate the docs: `make docs`.

### Commands:
- `$ sudo apt install pandoc pandoc-citeproc make`
- `$ make docs`


## nohup
If a terminal is closed (for example if you logout), a HUP signal is send to all programs that are running in the terminal. [@signals]
`nohup` is a command that executes a program, with intercepting the HUP signal. That results into the program doesn't exit when you logout.
The output of the program is redirected into the file `nohup.out`
`nohup` can be used with `&` to start a program in background that continues to run after logout. [@nohup]


## kubectl
`kubectl` is a command line tool that lets you control Kubernetes clusters.

## Kubernetes
Kubernetes is an open source container orchestration platform. With Kubernetes it's possible to automate deployments and easily scale containers. It has many features that make it useful for the project. Some of them are explained here. [@kubernetesredhat]

### Pods
A pod is a group of one or more containers that are deployed to a single node. The containers in a pod share an ip address and a hostname.

### Services
Services allows that service requests are automatically redirected to the correct pod.

### Control Plane
The control plane controls the Kubernetes cluster. It also has an API that can be used with kubectl or REST calls to deploy stuff. [@kubernetesredhat2]

### Deployment
Deployments define the applications life cycle, for example which images to use, the number of pods and how to update them. [@kubernetesredhatdeploy]

### Operators
[@kubernetesredhatoperator]

### Namespaces
