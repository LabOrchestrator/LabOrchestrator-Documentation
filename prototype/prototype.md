\pagebreak

# Prototype

In this chapter we will abstract the concepts of the last chapter and include them in a prototype. The prototype will add additional concepts like authentication and multi-user support. The prototype should be used to deploy labs and should on the one hand prove that this project is feasible and on the other hand serve as a template for the alpha phase.

## Deploying an API to the cluster TODO

The prototype will have an API and will be deployed with Kubernetes, so we first need an example API that will be deployed. For this we will use the [Flask Quickstart Example](https://flask.palletsprojects.com/en/2.0.x/quickstart/)^[https://flask.palletsprojects.com/en/2.0.x/quickstart/]:

~~~{#lst:exmplapi .py .long .numberLines caption="api.py" include=prototype/examples/hello_world_api/api.py}
~~~

Then we need to install all dependencies. For this we use the `requirements.txt`:

~~~{#lst:exmplrequirements .txt .long .numberLines caption="requirements.txt" include=prototype/examples/hello_world_api/requirements.txt}
~~~

The dependencies can be installed with the command `pip3 install -r requirements.txt`. Now this can be run with `python2 api.py`. Now open another terminal an make a request to the api: `curl localhost:5000`. The response should be `Hello, World!`.

After we have an API, we need to create a Docker Image that includes the API. For this we create a dockerfile. [@dockerpy]


~~~{#lst:exmpldockerfile .dockerfile .long .numberLines caption="dockerfile" include=prototype/examples/hello_world_api/dockerfile}
~~~

Then build and push it to docker hub: `docker build -t username/repo:version .` and `docker push username/repo:version`.

Now we have an API in a docker container in docker hub, that needs to be integrated in a pod. We will do this with a deployment and take the virtVNC deployment as base. We also need a service to connect to the API and we will run this in a different namespace called `lab-controller`. This will also be included in the yaml. [@kubevirtnovnc] [@k8sdeploy] [@kubernetesservice]

~~~{#lst:exmplapipod .yaml .long .numberLines caption="api-deploy.yaml" include=prototype/examples/hello_world_api/api-deploy.yaml}
~~~

Now we have our API running in Kubernetes. To test it, we can execute `minikube service --url helloworldapi -n lab-controller` and open the link in our browser. If the browser shows `Hello World` it has worked.

## Using the Kubernetes API TODO

So for now we have an hello world API running in our cluster that is accessible through a `NodePort`. Next we need to get access to the Kubernetes API.

### Authorization

To get access to the Kubernetes API from within a pod we need to create a `ServiceAccount` and to get access to different API resources we need to make use of the RBAC authorization. First move the namespace resource from `api-deploy.yaml` to its own file:

~~~{#lst:exmplns .yaml .long .numberLines caption="Example Namespace" include=prototype/examples/service_account_api/namespace.yaml}
~~~

Then add a yaml-file for the service account and the RBAC rules:

~~~{#lst:exmplsvcacc .yaml .long .numberLines caption="Example Service Account with RBAC" include=prototype/examples/service_account_api/serviceaccount.yaml}
~~~

The Listing [Example Service Account with RBAC](#lst:exmplsvcacc) first creates a `ServiceAccount` called `lab-controller-account`. This is the `ServiceAccount` we will use to connect to the API. Then it creates a `ClusterRole`, which contains permissions to access some API resources. This includes listing all KubeVirt VMs. Last it adds a `ClusterRoleBinding`, which binds the `ClusterRole` to the `ServiceAccount`. [@k8sserviceaccforpods] [@k8srbac] [@kubevirtnovnc] [@k8sauthenticating]

Next we need to update our deployment to use the `ServiceAccount` `lab-controller-account`. First we remove the Namespace creation if you not already have done this. Then we will add `serviceAccountName: lab-controller-account` to `spec.template.spec` as you see in Line 18. Adding the service account with this way adds a folder to the pod `/var/run/secrets/kubernetes.io/serviceaccount/` which contains the file `token` which is the token we need to use for making requests to the api which authenticates us, the file `namespace` which is the namespace we are in and the file `ca.crt` which is a certificate we need to use to make sure the connection to the Kubernetes API is secure. Notice that we have also changed the name of the deployment and pod to `serviceaccountapi`. [@k8saccesscluster]

~~~{#lst:scvaccdepl .yaml .long .numberLines caption="Example deployment with service account" include=prototype/examples/service_account_api/api-deploy.yaml}
~~~

Apply both yaml files to your Cluster. Then list you pods in the namespace `lab-controller` with `kubectl get pods -n lab-controller` and connect to the bash of the pod we have created with `kubectl exec --stdin --tty serviceaccountapi-deployment-RANDOM -- /bin/bash`. Now we are connected to our pod and try to access the Kubernetes API. [@k8saccesscontainer]

In the pod there are some environment variables that we need. The first is `$KUBERNETES_SERVICE_HOST` which gives us the IP address of the Kubernetes API and the second is `$KUBERNETES_SERVICE_PORT` which contains the port. This needs to be combined with the files from the service account folder. The following `curl` command will list all running VMIs: [@curlca] [@k8saccessapipod] [@k8saccesscluster]

~~~{#lst:curlapi .bash .long .numberLines caption="Getting all VMIs"}
curl \
    --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
    --header "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
    https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT/apis/kubevirt.io/v1alpha3/namespaces/default/virtualmachineinstances/ | \
    python -m json.tool
~~~

When you execute the command you should receive a list of VMIs if you have added any. If you don't have any running VMIs it looks like this:

![API access listing empty VMI list](./prototype/curlvmilist.png)


This can now be used in our `api.py`.

## Access the Kubernetes API in the Application

For now we have a simple hello world API application and we are able to access the Kubernetes API. This chapter is split up into three parts, will extend the prototype to first list all VMIs, then create new VMIs and last give us access to the console and VNC. In the first step we prepare the base that is needed to communicate with the Kubernetes API, i.e. reading the environment variables needed for configuration, reading the files containing the key, applying the ca cert. The second step extends the application with POST requests to create new resources. The challenge of the last step is that console and VNC uses websockets that we need to pass through the application and we need to serve the noVNC application.

The following chapters will explain what we have done to achieve the chapters goals and will split the source code of some files. You can read the full files [on github](https://github.com/LernmodulController/LernmodulController-Documentation/tree/master/prototype/examples/accessing_api)^(https://github.com/LernmodulController/LernmodulController-Documentation/tree/master/prototype/examples/accessing_api).

### Access API to list VMIs

For step one basic knowledge about flask and requests is required. You can get a quickstart into requests in the [requests quickstart](https://docs.python-requests.org/en/latest/user/quickstart/)^[https://docs.python-requests.org/en/latest/user/quickstart/] and a quickstart into flask in the [flask quickstart](https://flask.palletsprojects.com/en/2.0.x/quickstart/)^[https://flask.palletsprojects.com/en/2.0.x/quickstart/].

~~~{#lst:apistep1p1 .py .long .numberLines caption="api.py step 1 part 1" include=prototype/examples/accessing_api/api-step1.py startLine=1 endLine=38}
~~~

The [Listing api.py step 1 part 1](#lst:apistep1p1) shows us the first part of the `api.py` after we implemented the goals of step 1. First we have added a class `KubernetesAPI` that wraps the Kubernetes API. It takes the host and port, the token, ca cert and a boolean to disable verification of ssl. This class contains a generic method `get` that makes requests to the api and by automatically setting the base URL to the right host and port, setting the authentication method to bearer token and using the ca cert file if provided. Based on this generic method the `KubernetesAPI` class will be extended with methods that access resources. An example is `get_vmis`, which uses the `get` method to get all VMIs. [@pydocrequests] [@sorequestsnossl] [@sorequestscrt] [@sorequestscrt2]

~~~{#lst:apistep1p2 .py .long .numberLines caption="api.py step 1 part 2" include=prototype/examples/accessing_api/api-step1.py startLine=41 endLine=53 startFrom=41}
~~~

In [Listing api.py step 1 part 2](#lst:apistep1p2) the second part of the `api.py` is shown. The method `create_kubernetes_api_default` reads the host and port from environment variables and the file that contains the token and creates a variable with the location of the ca cert file. Then it creates a default instance of the `KubernetesAPI` that we can use in the flask routes.

~~~{#lst:apistep1p3 .py .long .numberLines caption="api.py step 1 part 3" include=prototype/examples/accessing_api/api-step1.py startLine=61 endLine=72 startFrom=61}
~~~

In [Listing api.py step 1 part 3](#lst:apistep1p3) the third part of the `api.py` is shown. Here we add another route to flask called `/vmis`. This route will return all VMIs of one namespace. For now we will only have access to VMIs in namespace default, but this will be changed in the next chapter: [User Support](#user-support). In this method the mimetype of the response is changed to `application/json`. In the response we return json and if we change the mimetype to json browsers, e.g. Firefox, will display them in comfortable way. [@soflaskjson] [@soflaskxml]

After the changes on the prototype you can rebuild and push the docker image and redeploy it to Kubernetes. You can get its URL with the command `minikube service --url serviceaccountapi -n lab-controller`. Now you can see a list of all VMIs that are running in the default namespace under `http://YOUR_URL:30001/vmis`. If you have no VMI running, you should start one to see an effect. To access the logs of your pod run the command `kubectl logs serviceaccountapi-deployment-RANDOM -n lab-controller`. [@k8sinteractpod]

![Application listing VMIs](./prototype/get_vmis.png)

The [Figure Application listing VMIs](#application-listing-vmis) shows the representation of `/vmis` in Firefox. This lists all VMIs currently running in the namespace default. As we see, there is one VMI running, the previously build `ubuntu-cloud-gnome`.

### Access the API to run new VMIs

### Access VNC

## User Support

[KubeVirt Authorization](https://kubevirt.io/user-guide/operations/authorization/)^[https://kubevirt.io/user-guide/operations/authorization/]

Because Kubernetes can be accessed through an API, we can wrap all methods in an application and add authorization in a different layer. This will be shown in the prototype.

Hier wird nach einer Lösung gesucht, womit es möglich ist mehrere user zu haben und dass ein user nur auf sein lab zugreifen kann.

Hier werden die vnc und ttyd dienste, welche wir nutzen über ingresses oder services nach außen erreichbar gemacht. Für vnc werden wir vermutlich einen proxy bauen müssen oder ähnliches um die k8 api zu wrappen.

