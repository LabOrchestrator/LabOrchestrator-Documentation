# Introduction

## Motivation
At the university, lecturers can simply provide their students with a VM in which the students can complete their assignments. In these VMs, software is pre-installed and pre-configured so that the students can, for example, directly start programming their microcontroller with the IDE provided. This has the advantage for the instructors that all students use the same system and therefore they only have to provide support for this system and do not have to worry about problems that vary from system to system. Also, the VM forms a sandbox and thus changes can be made to the system in this environment and if something breaks, a snapshot is taken or the original image is reinstalled.

However, the options here are limited to one VM and local deployment. It is not possible to simply start a whole network of VMs, nor is it possible to open these VMs in the browser.

## Description
The %project_name% shall allow to start a network of virtualised systems (i.e. VMs and different types of containers) and make them accessible over the network. In the network of virtualised systems several virtualised systems shall run simultaneously and if a user has access to one of the systems it shall be possible to access others. Several such networks should be able to be started, so that users can work independently of each other. A user has a user session and in this session a network is started for this user, in which the user can work.

The access to the virtualised systems should be possible via an integration in the web. The user should be able to start a network on a web page and then get access to the graphical user interface or the terminal of the virtualised systems in a frame or HTML canvas on the web page.

Furthermore, in addition to the integration as a frame or canvas, it should be possible to optionally integrate a tutorial. These instructions should be able to contain several pages and several steps per page and teach the person working in the virtualised system. The instructions contain various features, such as steps that can be checked to see the progress and tutorial boxes that provide knowledge and explain certain parts. These tutorials are meant to extend the mere sandbox to be able to teach people something.

As virtualised systems, we want to support docker containers and classic VMs.

## Target Groups
Target Groups:

- Universities
- Computer Science Clubs
- Companies
- IT Security Personal
- Learning Platforms
- Moodle

The software can be used in universities by lecturers to provide students with an environment in which they can learn and try out. On the one hand, it can be used parallel to lectures or practice sessions as a pure sandbox of a network in which students can do their exercises, and on the other hand, the tutorials can be integrated directly into the application.

Computer science clubs like the CCC often do Capture the Flag competitions. The program can make it easier to scale scenarios for competitions and learning.

Companies and private individuals can use the tool to map their internal IT environment and safely check their environment for security vulnerabilities in a sandbox. There is no need to consider any consequences for the live operation of the company.

IT security personnel also benefit from the sandbox environment and can be trained here or acquire their own knowledge. Although solutions such as Hack The Box already exist for this purpose, they cannot be hosted by the company itself and no instructions are available for them either.

Learning platforms can build on the program to create tutorials. Also an extension for Moodle, which is used by many universities, is conceivable, in which the courses of the application are integrated. One could use such a Moodle addon to work within Moodle in VMs and store tasks for students there.


## Project Planning
The %project_name% is divided into several parts:

- Orchestrator of virtualised systems
- Accessible from the Web Base Images
- %project_name% Library
- REST-API

### Orchestrator
Kubernetes is suitable as an orchestrator. Kubernetes allows you to launch a predefined set of Docker images. The images in a namespace can be connected to each other and ports can be opened to the outside. In Kubernetes' declarative YAML config, it is possible to define a set of Docker images, in addition to defining the ports opened to the outside and creating an internal network. This allows to access one container from another container. With such a config, it is easy to start and stop this set of containers as often as you want.

Kubernetes out of the box can only start containers. Here it is unclear whether the containers are sufficient to start graphical interfaces of Windows. The KubeVirt extension adds the function to use VMs instead of containers for this. KubeVirt can also be used to start a Windows VM with a graphical user interface. Kubernetes with KubeVirt therefore seems suitable as an orchestrator for the %project_name% .

### Accessible from the Web Base Images
In order to be able to access the virtualised systems from the web and to make it as easy as possible to create your own virtualised systems, a technology must be found that makes it possible to access the terminal or the graphical interface of the virtualised system. This technology should then be provided in a template for example a docker base image or an virtual machine image both with the tool preinstalled.

For terminal access, there are already various tools, such as Gotty, wetty and ttyd. For desktop access, there is Apache Guacamole and noVNC. It is necessary to evaluate which of these tools are the most suitable and then install and configure these tools in the base image.

The goal of this step is to have an runnable image where the graphical interface and the terminal of the VM or Docker container can be accessed via the web.

Then, this image must be included in a Kubernetes template so that a network of such virtualised systems can be launched in Kubernetes.

With this template, it must also be tested how it is possible to access it with multiple users. This will probably require a proxy that authorizes certain requests and forwards them to the respective containers. It must be evaluated how the authentication and the routing works. One possibility would be to include a token in the URL. This may work with Kubernetes out of the box, but if that is not enough there are other possibilities. Traefik for example is a dynamic proxy that automatically detects new services in Docker and integrates them for routing. Consul is another tool for discovering services. Traefik can interact with Consul and Consul can report the new routes to Traefik. The best solution here would be one where Traefik directly detects the routes from Kubernetes, similar to how it already works with Docker in Traefik. If that is not possible we either need to be able to add new routes via Traefik's API or include Consul. Anyway, with Consul it is possible to insert a dynamic configuration of routes afterwards. The insertion of new routes should only be tested manually in this step and then automated in the %project_name% Library. If this concept does not work with Traefik and Consul, we have to find another proxy possibility, program a new one or extend an already existing one with this function.

### %project_name% Library
The library is the core of the project and will be provided as a Python library. A network of virtualised systems base images is called a lab. The library should be able to manage the virtualised systems base images in Kubernetes and provide an interface to manage labs.

In the requirements list, "must" stands for that it has to be implemented, "should" is an optional requirement that should be implemented and "may" is an optional requirement that may be implemented.

Requirements for the library are:

- start and stop labs (must)
- pause and continue labs (should)
- add and remove labs (must)
- configuration of routing labs (must)
- authentication during routing (must)
- show authentication details in labs, e.g. login credentials (must)
- link users to their labs (must)
- add instructions (must)
- link labs and instructions (must)

Requirements for the instructions:

- Markdown or HTML syntax (should)
- pages with text (must)
- controller to select a virtualised system (must)
- steps per page (may)
- tick of steps (may)
- progress bar (may)
- progress bar for ticked steps (may)
- embed images and other media (should)
- present knowledge texts (must)
- interactions with virtualised systems, e.g. copy a text into the clipboard of a system (may)
- variables (may)

There is a Kubernetes client library for Python. This library can be used in the %project_name% to get access to the Kubernetes API and interact with Kubernetes.

Core functionalities of the library are start, stop, add and remove labs. To start and stop, the previously created template must be mapped into the Kubernetes Client Library and some settings such as the namespace must be kept variable. The Client Library can then be used to start and stop the templates. The configuration of the templates must be stored in a database and contain among other things the access token, the user ID and the specific template configuration like the namespace which is used.

For adding new labs, it is intended that one provides a path to the images of the VMs or, in the case of Docker, optionally a link to the image in a container registry. The specified VMs or containers are then added to the template and must have the respective terminal/desktop web solution integrated and properly configured. Additional Kubernetes configuration can also be entered here. The configuration is then stored in the database. To remove a lab, only the configuration then needs to be deleted from the database.

Pause and continue labs would be a useful extension, which, however, is not mandatory for the first version.

Depending on the routing and authentication solution from the previous step, the proxy must still be told how to use the ports of the VMs or containers when a lab is started. If the Kubernetes native solutions doesn't work, either the Traefik API or Consul must be used. These routing settings must be included in the response at startup so that users know which URL they can use to access it. There must also be a possibility to select the different containers in the URL.

An authorization who can start labs is not provided here and comes in the web interface with a proper user management. That means, everyone who uses this library can do everything in the code and must add an authorization layer, if certain labs are to be started only by certain users.

To link the users with their labs it is sufficient to store a user ID and optionally a name for the user, which can optionally be included in the instructions via variables.

The instructions are only texts, which have to be stored in the database. Several pages can be stored in different database entries or the complete instruction of a course can be stored in one database entry. These are then linked to the respective lab template. All but four features of the instructions are requirements to be implemented in the web interface and are simply different representations of the text. The controller for selecting the virtualised system can include the URLs from the response at startup, as links for the frame. So that individual steps can be checked off, another database table must be added under circumstances, which stores the status. Variables could be queried via an extra function and then also composed by the web interface. For the interaction with the virtualised system, existing solutions can be searched for or an interface for this must be integrated in the virtualised system. The simplest possibility for this would be to offer a service via an internal web interface in the virtualised system, which copies texts into the clipboard.

It must also be evaluated whether the library should write data to a database on its own or only return the data that needs to be saved as a response. The former would be more trivial to use and a SQLite database would be a good choice. The second would provide more flexibility and it would be easier to integrate into Django.


### REST-API
The library alone offers the advantage that you can easily write programs that use this concept. For example, you can include the library in a Django app or in desktop software. Another use case for the library would be a web interface to control the library. This way you can include the library in a microservices system or you can access it from other programming languages and thus include it in many other non-Python projects. The web interface will be a REST-API and will be implemented with Django or Flask.

The library will not yet have authentication to start labs, only authorization when accessing the labs. In the web interface the library will be extended by a permission system and user management. Otherwise, the web interface only has to offer the functionalities of the library via REST.

## Milestones

### Proof of Concept and Prototype
First we need to understand the concepts of Kubernetes and find a way to to deploy labs. This is done in the proof of concept. After that we will include this in a prototype that should proof that the idea of labs is possible.

1. Install Kubernetes and KubeVirt
2. Understand basics of Kubernetes and Kubernetes templates
3. Understand how to start and stop Kubernetes templates, base images and VMs
4. Evaluation of web-terminal and web-vnc tools
5. Integration of web-terminal and web-vnc tools into base images and VMs
6. Integrate base images and VMs into Kubernetes templates
7. Evaluate and implement a routing solution
8. Add multi-user support to the routing solution

In this step Kubernetes and maybe KubeVirt will be installed and configured. We will take a look at Kubernetes templates and base images and how they can be started and stopped in Kubernetes. This is the basic knowledge we need to build the application.

After that, we will evaluate which web-terminal tool and which web-vnc tool is the most suitable for using in the base images. And afterwards this tools will be integrated into docker base images or VM base images. These will be the basis of the labs.

The base images will be integrated into a Kubernetes template and combined with a basic routing solution. After that works the routing will be extended to support multi-user labs.

If all that steps work, the prototype will be a success. This proves, that the orchestrator can be implemented with Kubernetes and the given web accessible base images.

### Alpha Phase
Then in the alpha phase the %project_name% library will be implemented.

1. Start and stop labs
2. Automatically add routing and authorization
3. Add and remove labs
4. Add and remove instructions
5. Link users to labs
6. Link instructions to labs

At the end of the alpha phase we have a working solution as library, that fulfills the minimal needed set of requirements. This library can than be used in other project for example the REST-API.

### Beta Phase
In the Beta Phase we will add the REST-API and add the remaining optional features.

1. Implement a REST-API that is able to use the library to start and stop labs
2. Add user-management and permission system to the REST-API
3. Add remaining features of the instructions
4. Pause and continue labs

After the beta phase has succeeded, the project is considered finished and can be released to the public.
