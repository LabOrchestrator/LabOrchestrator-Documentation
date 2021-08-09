\pagebreak

# Prototype

In this chapter we will abstract the concepts of the last chapter and include them in a prototype. The prototype will add additional concepts like authentication and multi-user support. The prototype should be used to deploy labs and should on the one hand prove that this project is feasible and on the other hand serve as a template for the alpha phase.

## Deploying an API to the cluster

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

## Using the Kubernetes API

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

First we need to know how to create and delete VMIs over the Kubernetes API. The [Kubernetes API Overview](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.19/)^[https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.19/] gives us a good overview about how to get, create, replace and delete Kubernetes objects. What's missing there are the KubeVirt resources, but the concepts are the same. You get all objects of a resource with a GET request to the resource URI as we already know. To get a specific object you need to make a GET request to the object URI (resource uri + /name-of-object). To create new objects the request must make a POST request to the resource URI. The object data needs to be attached in the body and the header `Content-Type` must describe the format of the body. Accepted formats are yaml, json and protobuf. To delete an object you need to get the URI to the object and make a DELETE request. [@k8sapioverview]

To test this, we start `kubectl proxy` and try creating and deleting a VMI with curl.

~~~{#lst:curlcreatevmi .bash .long .numberLines caption="curl create vmi"}
curl \
    -X POST \
    --data-binary @"ubuntu_cloud_gnome.yaml" \
    -H "Content-Type: application/yaml" \
    http://localhost:8001/apis/kubevirt.io/v1alpha3/namespaces/default/virtualmachineinstances/
~~~

~~~{#lst:curlcreatevmi2 .bash .long .numberLines caption="curl create vmi 2"}
curl \
    -X POST \
    --data "$(cat ubuntu_cloud_gnome.yaml)" \
    -H "Content-Type: application/yaml" \
    http://localhost:8001/apis/kubevirt.io/v1alpha3/namespaces/default/virtualmachineinstances/
~~~


~~~{#lst:ubuntu_cloud_gnome .yaml .long .numberLines caption="ubuntu_cloud_gnome.yaml" include=prototype/examples/accessing_api/ubuntu_cloud_gnome.yaml}
~~~

[Listing curl create vmi](#lst:curlcreatevmi) shows a curl command that creates a VMI. It attaches the content of the file in [Listing ubuntu_cloud_gnome.yaml](#lst:ubuntu_cloud_gnome) to the body and sets the header `Content-Type` to `application/yaml`. When we run `kubectl get vmi` a new VMI is shown. [Listing curl create vmi 2](#lst:curlcreatevmi2) does the same but it doesn't attach the file but attaches the file contents as string. This will have a benefit when implementing it in python, because we can generate the yaml string in python without saving it to a file. [@socurldata]

~~~{#lst:curldeletevmi .bash .long .numberLines caption="curl delete vmi"}
curl \
    -X DELETE \
    http://localhost:8001/apis/kubevirt.io/v1alpha3/namespaces/default/virtualmachineinstances/ubuntu-cloud-gnome
~~~

[Listing curl delete vmi](#lst:curldeletevmi) shows a curl command that deletes the VMI that we have created before. When we run `kubectl get vmi` the VMI is succeeded or not displayed anymore.

Now we add this to the application, but first we need to extend the permission of our service user, because for now it is not allowed to create VMIs. In the next step we want to create and delete VMIs so we need to add `create` and `delete` to the ClusterRole of our ServiceAccount.

~~~{#lst:createdeleterole .yaml .long .numberLines caption="serviceaccount_version2.yaml" include=prototype/examples/accessing_api/serviceaccount_version2.yaml startLine=7 endLine=33 startFrom=7}
~~~

[Listing serviceaccount_version2.yaml](#lst:createdeleterole) shows the changed ClusterRole that contains create and delete permissions. This needs to be applied. [@k8srbac]

Now we will add a VMI template to the docker image. This is used to deploy VMIs later.

~~~{#lst:vmitemplate .yaml .long .numberLines caption="vmi_template.yaml" include=prototype/examples/accessing_api/vmi_template.yaml}
~~~

The template in [Listing vmi_template.yaml](#lst:vmitemplate) contains some variables: `${namespace}`, `${vmi_name}`, `${cores}`, `${memory}` and `${vm_image}`. `namespace` is the namespace this VMI is deployed to. `vmi_name` is its name. `cores` and `memory` are used to specify how much memory and cores the machine can use. `cores` needs to be an integer otherwise the api will throw an error. `vm_image` is the image location of our docker hub image in the format `USERNAME/REPO:VERSION`.

This needs to be added to the dockerfile if you don't copy all files from this directory in it. Also add `pyyaml` to the `requests.txt`.

After that we extend our `KubernetesAPI` class with delete and create possibilities, add new routes and a yaml template engine.

~~~{#lst:apicreatedelete .py .long .numberLines caption="api-step2.py part 1" include=prototype/examples/accessing_api/api-step2.py startLine=42 endLine=77 startFrom=42}
~~~


The [Listing api-step2.py part 1](#lst:apicreatedelete) shows us the part of the KubernetesAPI that we have added. It contains four new methods: `post`, `create_vmi`, `delete` and `delete_vmi`. `post` and `delete` are two more generic methods that can be used to create and delete objects. To use the `post` method you need to add the data of the object in the yaml format. The `delete` method can delete resources. Due to currently missing permissions it's only possible to delete single objects and no collections, but the method will delete both when you add the correct permissions to the service account. The methods `create_vmi` and `delete_vmi` just prepares the URLs and then calls the generic methods.

~~~{#lst:apitemplate .py .long .numberLines caption="api-step2.py part 2" include=prototype/examples/accessing_api/api-step2.py startLine=95 endLine=121 startFrom=95}
~~~

The [Listing api-step2.py part 2](#lst:apitemplate) shows the template engine. The template engine can read a yaml file and replace yaml variables with values from python variables. For this you need to create an object of the `TemplateEngine` and pass a data object into the class. This data object needs to be a dictionary that contains all variable names and its values. Then you can call the `load_yaml` method with the filename of the yaml file which gives you a yaml object with replaced variables. Alternatively you can directly call the `replace` method which will return the yaml as string instead of object. This is what we need for our creation of Kubernetes objects. [@sopyyamlreplace] [@pyyamldoc] [@sopyyamlint]

~~~{#lst:apicreatedeleteroutes .py .long .numberLines caption="api-step2.py part 3" include=prototype/examples/accessing_api/api-step2.py startLine=137 endLine=160 startFrom=137}
~~~

Last but not least in [Listing api-step2.py part3](#lst:apicreatedeleteroutes) we can see the new routes. The first route is `/create_vmi`. In this method `request.args` is used to get the VMI name and the VM image location in docker hub from URL arguments. Then a dictionary is created that contains all key-value pairs that are needed for our template and a TemplateEngine object is initialized with this dictionary. Next the `replace` method gives us a string of the yaml template with all variables replaced with the values from the dictionary. This string is used to create a VMI with the `create_vmi` method. The `/delete_vmi` route is not that spectacular, it just gets an URL argument and calls the `delete_vmi` method. [@soflaskurlparam]

Build the image, push it and recreate the pod. Now we have implemented the create and delete feature for VMIs. We are able to create VMIs with opening this URL in the browser: `http://192.168.50.45:30001/create_vmi?vmi_name=ubuntu-cloud-gnome2&vm_image=USERNAME/REPO:VERSION` (replace the CAPSCASE with your VM image). This creates a VMI with the name `ubuntu-cloud-gnome2` and the VM image you specified. The VMI will be deployed to the default namespace. With `kubectl get vmi` you can see another VMI starting in our cluster. After it has started we can delete it with opening: `http://192.168.50.45:30001/delete_vmi?vmi_name=ubuntu-cloud-gnome2`. All in all this is a bad API design, but it's enough for the prototype.

### Access VNC

First we need to create a websocket proxy in python, that creates one websocket connection to the Kubernetes api and another to the noVNC client that is accessible over the api. In the middle of this we can add our authentication. For the proxy we will use an [example from github](https://gist.github.com/bsergean/bad452fa543ec7df6b7fd496696b2cd8)^[https://gist.github.com/bsergean/bad452fa543ec7df6b7fd496696b2cd8] and modify it. [@ghgwebsocketproxy] [@websocketspy]

~~~{#lst:wsproxyp1 .py .long .numberLines caption="ws_proxy-step3.py part 1" include=prototype/examples/accessing_api/ws_proxy-step3.py startLine=1 endLine=28}
~~~

`TOKEN_DB` and the methods `add_token` and `check_token` are used as simple authentication mechanism. If a token is included in this list and associated with the VMI name, then the user is allowed to access the VNC. This may be changed in the next chapter. `add_token` is used to add credentials to the database.

~~~{#lst:wsproxyp2 .py .long .numberLines caption="ws_proxy-step3.py part 2" include=prototype/examples/accessing_api/ws_proxy-step3.py startLine=31 startFrom=31 endLine=55}
~~~

We have moved the code from the above example into a class called `WebsocketProxy`. During initialization you need to pass a `remote_url` and an `api_path`. The `api_path` needs to have `"{vmi_name}"` included because with `str.format` this will be inserted. With our Kubernetes API the `api_path` needs to be `"/apis/subresources.kubevirt.io/v1alpha3/namespaces/default/virtualmachineinstances/{vmi_name}/vnc"`. The method `run` will run the `ws_proxy` in foreground and block the python main thread. `run_in_thread` will run the `ws_proxy` in another thread so it won't block the main thread. This is needed because our main thread is used by flask. `stop_thread` is needed to stop the thread if the program is to be terminated.

~~~{#lst:wsproxyp3 .py .long .numberLines caption="ws_proxy-step3.py part 3" include=prototype/examples/accessing_api/ws_proxy-step3.py startLine=57 startFrom=57 endLine=92}
~~~

The method `proxy` is called whenever a new connection to the `ws_proxy` is made. This method first checks the authentication. This is done by splitting the path by a divider and taking the first argument as VMI name and the second as token. This is a useful authentication, because in noVNC we can only specify the path and not for example special headers or other authentication mechanisms. So because of noVNC we are limited to make authentication with this trick. After authentication was successful the method opens a new websocket to the Kubernetes API. There are two ways for this, one is with SSL, where also the self signed certificate is included and the bearer token is attached. And a second way for local development without this. After that every message that is send to the `ws_proxy` within this websocket connection is redirected to the Kubernetes API and the other way around as well. So at this point we have two websocket connections: first client to `ws_proxy` and second `ws_proxy` to Kubernetes. These connections are kept alive and only the messages are redirected. [@ghgwebsocketproxy] [@websocketspy] [@soasynciothread] [@pydoceventloop] [@sobug1] [@sobug2] [@soflaskthread] [@rtdwebsockets] [@sosecwebsock] [@sosecwebsock2]

~~~{#lst:wsproxyp3 .py .long .numberLines caption="ws_proxy-step3.py part 3" include=prototype/examples/accessing_api/ws_proxy-step3.py startLine=94 startFrom=94 endLine=100}
~~~

The next two methods are just methods that redirect the traffic between the websockets. [@ghgwebsocketproxy] [@websocketspy]

~~~{#lst:wsproxyp4 .py .long .numberLines caption="ws_proxy-step3.py part 4" include=prototype/examples/accessing_api/ws_proxy-step3.py startLine=103 startFrom=103 endLine=112}
~~~

The line `if __name__ == '__main__':` checks if the file is executed directly or if it is included in another code. So this part only is executed if you run `python3 ws_proxy.py` and not if you include it in `api.py` and run `python3 api.py`. This is useful for development and testing of the module.

We will save our websocket proxy in an extra file `ws_proxy.py` for more modularity. We can later include it into the `api.py`. Now we can start the proxy with `python ws_proxy.py`. Now if we start a connection to `localhost:8765/VMI_NAME/TOKEN` this proxy creates a connection to the Kubernetes api to the VNC websocket from the VMI with name `VMI_NAME`. The token is then checked if you have the correct rights to connect to this VMI.

Now if we start the noVNC server with `python -m SimpleHTTPServer` we can access the proxied websocket at: `http://localhost:8000/vnc_lite.html?host=localhost&port=8765&path=ubuntu-cloud-gnome/supersecret`. If you change the token you won't get access. So as we see our websocket proxy is working and now we need to include it in the `api.py`.

First we will move the `TemplateEngine` into its own file `template_engine.py`. And then make some changes to the `api.py` so that we can run it with `kubectl proxy` which will simplify development. I will not go into details here, you can check the difference of the steps by yourself with `diff api-step1.py api-step2.py`.

~~~{#lst:apistep3 .py .long .numberLines caption="api-step3.py part 1" include=prototype/examples/accessing_api/api-step3.py startLine=123 startFrom=123 endLine=131}
~~~

This new route is used to add credentials that we need to connect to the VNC.

~~~{#lst:apistep3 .py .long .numberLines caption="api-step3.py part 2" include=prototype/examples/accessing_api/api-step3.py startLine=134 startFrom=134 endLine=149}
~~~

First we have added a dictionary that contains some configuration for example the ports that should be used for `ws_proxy` and flask. This will later be changed to use environment variables. After that there is the method `run`, which will start the `ws_proxy` and flask and shuts the `ws_proxy` down after flask stopped.

~~~{#lst:deploy3 .py .long .numberLines caption="api-deploy-step3.yaml" include=prototype/examples/accessing_api/api-deploy-step3.py startLine=17 startFrom=17}
~~~

We have (the last time) renamed the deployment and added the new port 5001.

Now add `websockets` to the `requirements.txt`. Then add the new files to the dockerfile and rebuild and push the docker image. Then update it in Kubernetes and open it.

Then we can call `minikube service --url lab-controller-api -n lab-controller` to get the URLs. We need to add our credentials with this URL:  
`192.168.50.45:30001/add_credentials?user=marco&token=geheim&vmi_name=ubuntu-cloud-gnome`

After that we can access the VNC in:  
`http://localhost:8000/vnc_lite.html?host=192.168.50.45&port=30002&path=ubuntu-cloud-gnome/geheim`

## User Support

In this chapter we will finish the prototype, make a refactoring of the old code and add user support. One feature that is not included is accessing the console but this will be added in the alpha.


### Refactoring

The KubernetesAPI was refactored and put into its own module called `kubernetes`. Before the refactoring, every Kubernetes API endpoint needed to be added into the KubernetesAPI class. Now you can write extensions and only need to add a class with the api URLs and register the class with an decorator. After the class is registered you can access it in the APIRegistry as a property. For example `APIRegistry(...).namespace` or `APIRegistry(...).virtual_machine_instances`.

~~~{#lst:final_kube_api_1 .py .long .numberLines caption="kubernetes/api.py Proxy" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/api.py startLine=25 startFrom=25 endLine=58}
~~~

The KubernetesAPI class is renamed into Proxy. This class sends request to the Kubernetes api and adds required headers and verifies the right certificate.


~~~{#lst:final_kube_api_2 .py .long .numberLines caption="kubernetes/api.py ApiExtension" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/api.py startLine=73 startFrom=73 endLine=106}
~~~

The api has two different types of API endpoints. The ones that only work with namespaces and the other that doesn't have a namespace. For example a namespace is a not namespaced resource and an VMI is a namespaced resource. The difference between these two types is how you build the URL. Every type has an identifier, but namespaced URLs has an namespace too. The ApiExtension class contains the basics for all api extensions and the NamespacedApi and NotNamespacedApi extends this to provide the two types of API endpoints. With this two abstract classes we are able to add any Kubernetes API endpoint to our library. [@k8sdocapi]

~~~{#lst:final_kube_api_3 .py .long .numberLines caption="kubernetes/api.py Extensions" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/api.py startLine=109 startFrom=109 endLine=124}
~~~

The [listing kubernetes/api.py Extensions](#lst:final_kube_api_3) shows three extensions we have added. One for the namespace resource, one for the VMIs and one for network policies. With this three extensions we are able to create, delete and get any of these resources. The extensions are registered with the decorators `add_api_not_namespaced` and `add_api_namespaced`. Without adding these decorators we are not able to use this extensions.

~~~{#lst:final_kube_api_4 .py .long .numberLines caption="kubernetes/api.py decorators" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/api.py startLine=7 startFrom=7 endLine=22}
~~~

The methods `add_api_namespaced` and `add_api_not_namespaced` return the decorators. Decorators are methods that get a function or class passed as argument. The return value of the decorator will replace the decorated function or class. So with decorators you are able to replace a function or class with another function. We use decorators here to add the passed class to a dictionary. The key of the dictionary is the string passed into the outer function, i.e. `namespace` in the Namespace Extension and network_policy in the NetworkPolicy Extension. The value is a reference to the class. We have two dictionaries here: one for the namespaced extensions and one for the not-namespaced extensions. The decorators return the same as they got passed into so that the function or class will not be replaced.

~~~{#lst:final_kube_api_5 .py .long .numberLines caption="kubernetes/api.py APIRegistry" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/api.py startLine=61 startFrom=61 endLine=70}
~~~

The `APIRegistry` can be initialized with an object of the `Proxy`. This class makes use of the magic method `__getattr__`. In python when you call a method or get an attribute of an object, python executes the method `__getattribute__` with the name of the method or attribute as parameter if this method is defined. If `__getattribute__` is not defined python will look if the class has this attribute or method itself. If that is not the case, python will execute the `__getattr__` method if it is defined. With defining one of this methods you can dynamically process attributes. In the `APIRegistry` this is used to add new attributes to the class for every extension class that is in the dictionaries. Every `add_api_namespaced` decorator will add an attribute to this class with an instance of the decorated class. So if you want to create a namespace you can simply call `APIRegistry(...).namespace.create(...)` or if you want to get all VMIs you can call `APIRegistry(...).virtual_machine_instances.get_list(...)`.

~~~{#lst:final_model .py .long .numberLines caption="model.py" include=prototype/examples/user_support/lab_orchestrator_prototype/model.py startLine=6 startFrom=6 endLine=28}
~~~

We are using SQLAlchemy as ORM and added some database classes. The first class is `DockerImage`. This class contains a name, a description and a URL. This can be used to add docker images to the lab orchestrator which can later be injected into a VMI template. This makes creating labs easy, because you only need to have the URL to your docker image. The second class is `Lab` which contains a name, a namespace prefix, a description, a reference to a docker image and a name for the docker image. The namespace prefix is used to create namespaces when launching a lab and to separate this from other labs. That's the reason this needs to be unique. If you add a new lab you need to make sure your namespace prefix doesn't include characters that are not allowed in Kubernetes namespaces. The docker image is a reference to the first class and the idea ist that you can use a docker image for many labs if you don't need a custom image. For example you can create many labs that just use the default ubuntu image. The name of the docker image is used as VMI name and when adding new labs you need to make sure this doesn't include characters that are not allowed in Kubernetes VMI names. The third class is `LabInstance`. A lab instance is a lab that was started by a user, tho this class only references the user and the lab. [@sqlalchrela] [@flaskalchemy] [@alchemymodels]

Next we come to the controllers module. The controllers are used to group some services together and provide them in a central interface. They are used in the routes to access objects in the database model and the Kubernetes API. There are two types of main-controllers: `ModelController` and `KubernetesController`. The `KubernetesController` is further divided into two types: `NamespacedController` and `NotNamespacedController` so there is a total of three base classes that will be used.

~~~{#lst:final_controller_1 .py .long .numberLines caption="kubernetes/controller.py ModelController" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=14 startFrom=14 endLine=43}
~~~

The `ModelController` is a controller that adds methods for database models. When extending this class you need to implement the methods `_model` and `_serialize`. `_model` needs to return the model class and `_serialize` needs to return a dictionary that can be used to serialize the objects and return them as JSON in the API. When extending this class you are automatically able to get a list of all items in the database table, you can get a specific object by its identifier and you can delete objects. There is also a create method that can be used to create new objects. The last method provided in this base class is `make_response`, which is used in the routes and returns a jsonified version of the object or a list of objects. [@flaskalchemy] [@soalchemyget] [@alchemyquery]

~~~{#lst:final_controller_2 .py .long .numberLines caption="kubernetes/controller.py KubernetesController" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=46 startFrom=46 endLine=59}
~~~

The `KubernetesController` class makes use of the `TemplateEngine` and the `APIRegistry` to provide methods for Kubernetes api resources. The `make_response` method turns the string from the Kubernetes API into a response and adds the `application/json` mimetype.

~~~{#lst:final_controller_3 .py .long .numberLines caption="kubernetes/controller.py Namespaced- and NotNamespacedController" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=62 startFrom=62 endLine=87}
~~~

The `NamespacedController` and `NotNamespacedController` extend the `KubernetesController` to provide methods for the two types of Kubernetes API endpoints. This classes adds methods to get a list of all objects, get a specific object by its identifier and delete an object by its identifier. If you extend these classes you need to implement the `_api` method. This method needs to return the API extension class this controller should work onto.

~~~{#lst:final_controller_4 .py .long .numberLines caption="kubernetes/controller.py NamespaceController" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=90 startFrom=90 endLine=99}
~~~

~~~{#lst:namespacetemplate .yaml .long .numberLines caption="templates/namespace_template.yaml" include=prototype/examples/user_support/templates/namespace_template.yaml}
~~~

The `NamespaceController` implements the `NotNamespacedController` and adds the template for namespaces and a create method.

~~~{#lst:final_controller_5 .py .long .numberLines caption="kubernetes/controller.py NetworkPolicyController" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=102 startFrom=102 endLine=115}
~~~

~~~{#lst:networkpolicytemplate .yaml .long .numberLines caption="templates/network_policy_template.yaml" include=prototype/examples/user_support/templates/network_policy_template.yaml}
~~~

The `NetworkPolicyController` implements the `NamespacedController` and adds the template for network policies and a create method. Because you only add one of these network policies to a namespace the network policy name has a default value and can't be changed.

~~~{#lst:final_controller_6 .py .long .numberLines caption="kubernetes/controller.py DockerImageController" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=118 startFrom=118 endLine=126}
~~~

The `DockerImageController` implements the `ModelController` and adds a create method.

~~~{#lst:final_controller_7 .py .long .numberLines caption="kubernetes/controller.py VirtualMachineInstanceController" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=129 startFrom=129 endLine=152}
~~~

~~~{#lst:virtualmachineimagetemplate .yaml .long .numberLines caption="templates/vmi_template.yaml" include=prototype/examples/user_support/templates/vmi_template.yaml}
~~~

The `VirtualMachineInstanceController` implements the `NamespacedController` and adds a create method and some special methods. The create method adds some preconfigured variables to the template data like amount of cores and size of the memory. For now this can't be changed, but it would be easy to make it customizable. The name of the VMI is taken from the `docker_image_name` attribute of the lab object from which the VMI will be generated. The URL from where the docker image is taken is taken from the referenced docker image of the lab. The method `get_list_of_lab_instances` is used to find all instances of a given lab instance. This is useful to find the VMIs of your currently started Lab. The method `get_of_lab_instance` does the same, but only returns the specified VMI if it is contained in the lab instance. This is used for the details page in the API.

~~~{#lst:final_controller_8 .py .long .numberLines caption="kubernetes/controller.py LabController" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=160 startFrom=160 endLine=171}
~~~

The `LabController` implements the `ModelController` and adds a create method.

~~~{#lst:final_controller_9 .py .long .numberLines caption="kubernetes/controller.py LabInstanceController 1" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=174 startFrom=174 endLine=197}
~~~

~~~{#lst:final_controller_10 .py .long .numberLines caption="kubernetes/controller.py LabInstanceController 2" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=199 startFrom=199 endLine=219}
~~~

The `LabInstanceController` implements the `ModelController` and adds many methods. There are two static methods that can be used to generate the namespace name the lab is running into. Then a create method is added. The create method first creates the lab instance in the database. Then it generates the namespace name and creates the new namespace. After that the network policy and the VMI are created in this namespace. This method contains no error handling so it may not work without notifying you if you for example configured a wrong namespace prefix. After the create method the delete method is overwritten. It deletes the database object and then deletes the namespace where the VMI and network policy is running in. With deleting the namespace every resource in this namespace gets deleted too. The last method is `get_list_of_user` which returns a list of lab instances that belong to the given user.

~~~{#lst:final_controller_11 .py .long .numberLines caption="kubernetes/controller.py ControllerCollection" include=prototype/examples/user_support/lab_orchestrator_prototype/kubernetes/controller.py startLine=222 startFrom=222 endLine=229}
~~~

The `ControllerCollection` doesn't implement any controller base class. This class is only used to have a collection with every controller. An object of this class is used in the routes to get access to the controllers.

The module `routes` contains the API routes. We have removed the old routes and added new routes. The routes are based on the Rest API design and are able to read the parameters from the POST body or URL query parameters. [@soflaskdata] [@wikihttpcodes] You have the following URLs:

- `/lab_instance`: GET, POST
    - Users can see their lab instances
    - Users can create new lab instances
- `/lab_instance/<int:lab_instance_id>`: GET, DELETE
    - Users can see details to their lab instances
    - Users can delete their instance
- `/lab_instance/<int:lab_instance_id>/virtual_machine_instances`: GET
    - Users can see their VMIs
- `/lab_instance/<int:lab_instance_id>/virtual_machine_instances/<string:virtual_machine_instance_id>`: GET
    - Users can see details to their VMIs
- `/docker_image`: GET, POST
    - Everyone can see the docker images
    - Admins can create new docker images
- `/docker_image/<int:docker_image_id>`: GET, DELETE
    - Everyone can see details to the docker images
    - Admins can delete docker images
- `/lab`: GET, POST
    - Everyone can see the labs
    - Admins can add new labs
- `/lab/<int:lab_id>`: GET, DELETE
    - Everyone can see details to the lab
    - Admins can delete labs

The methods in the routes uses the services in the Controllers in the `ControllerCollection` object and adds permissions. The last method in this module is only needed to load this module. Every route is added to the app with decorators and they are only executed if this module is loaded.

The module `app` contains the flask app, the `SQLAlchemy` database object, the authentication objects, some basic configuration and a singleton class for the `ControllerCollection` object that is used in the routes. [@flaskconfig]

~~~{#lst:final_ws_proxy_1 .py .long .numberLines caption="ws_proxy.py 1" include=prototype/examples/user_support/lab_orchestrator_prototype/ws_proxy.py startLine=13 startFrom=13 endLine=15}
~~~

~~~{#lst:final_ws_proxy_2 .py .long .numberLines caption="ws_proxy.py 2" include=prototype/examples/user_support/lab_orchestrator_prototype/ws_proxy.py startLine=44 startFrom=44 endLine=65}
~~~

In the `ws_proxy` module we first removed the old authentication methods and replaced it with the JWT token authentication that we have added in the `user_management` module which we will explain in a moment. The `proxy` method has also some changes. The path now contains the id of the lab instance and a JWT token. The id is used to get the lab instance and the lab. This is needed to get the namespace name where the VMI is running and the VMI name. Both are needed to generate the VNC remote URL.

Last part of the refactoring is the `api` module. Here we load the config from environment variables and setup the `Proxy` and `APIRegistry` object and the Controllers. After that the `ws_proxy` and flask app are started. [@flaskconfig]

In addition to this we have added a new start script `run`. To execute it set the necessary environment variables and execute the script with `./run` or `python3 run`.

### User Management

In this step we have added a user class and authentication methods. To achieve this the [blog of miguel grinberg](https://blog.miguelgrinberg.com/post/restful-authentication-with-flask)^[https://blog.miguelgrinberg.com/post/restful-authentication-with-flask] was used. The full code of miguelgrinbergs example can be found [on github](https://github.com/miguelgrinberg/REST-auth)^[https://github.com/miguelgrinberg/REST-auth] MIT licensed. [@ghrestauth] [@grinbergblog]

~~~{#lst:final_user_mgmt_1 .py .long .numberLines caption="user_management.py 1" include=prototype/examples/user_support/lab_orchestrator_prototype/user_management.py startLine=12 startFrom=12 endLine=38}
~~~

The `User` class add the possibility to save users. Users have an id, an username and password and can be an admin. The `hash_password` method saves the password hashed to the database and the `verify_password` is able to verify this hash. `generate_auth_token` is used to generate a JWT token and `verify_auth_token` is used to verify this token during login.

~~~{#lst:final_user_mgmt_2 .py .long .numberLines caption="user_management.py 2" include=prototype/examples/user_support/lab_orchestrator_prototype/user_management.py startLine=41 startFrom=41 endLine=54}
~~~

The method `create_admin` checks if the user with the given username is already created. If the user is created its admin status and password will be changed. If the user is not created it will be created with admin status and password.

~~~{#lst:final_user_mgmt_3 .py .long .numberLines caption="user_management.py 3" include=prototype/examples/user_support/lab_orchestrator_prototype/user_management.py startLine=58 startFrom=58 endLine=68}
~~~

The method `verify_password` is added to the authentication object and used for authentication in flask. The method is able to check two different ways of authentication. One is username and password authentication and the other is token based authentication. This is both used with basic-auth. If you want to login with the token and basic auth, you need to pass the token as username and give a random password. The password is ignored if you use token based authentication. It may be better to use bearer token authentication for token based authentication instead of basic-auth.

After this there are some routes added to the flask app:

- `/api/users`: POST
    - creates a new user
- `/api/users/<int:id>`: GET
    - returns information about a user
- `/api/token`: GET
    - Users can generate a JWT token with this method. This is needed for token based authentication and the authentication in the VNC part

## Results

Now we have an API where we can create users and authenticate with two different methods: username/password authentication and token authentication which uses JWT tokens.

**Create User and Authenticate**

Create a user: [@sopostjson]

~~~{#lst:curlcreateuser .bash .long caption="create user with curl"}
curl \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"username": "me", "password": "secret"}' \
    localhost:5000/api/users
~~~

Authenticate with username/password:

~~~{#lst:curlbasicauth .bash .long caption="username/password authentication with curl"}
curl \
    -u me:secret \
    localhost:5000/lab_instance
~~~

Get token:

~~~{#lst:curlgettoken .bash .long caption="get a token with curl"}
curl \
    -u me:secret \
    localhost:5000/api/token
~~~

The response should look like this:

~~~{#lst:curltokenresposne .json .long caption="JWT token response"}
{
  "duration": 600,
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MSwiZXhwIjoxNjI4MjYyNDE5LjY4NDU3NDR9.lo3MsKr8iQXM0fnd06EmU97vo6iwggx49p3W1FOTaWc"
}
~~~

Copy the token from the response and authenticate with token:

~~~{#lst:curllogintoken .bash .long caption="token authentication with curl"}
curl \
    -u TOKEN:unused \
    localhost:5000/lab_instance
~~~

**Add docker images**

There is an admin account that will be created during the startup. Its default username is `admin` and password is `changeme`. You can change this with environment variables. To create a lab and add docker images you need to have admin rights so you need to use this default user.


First upload your docker image to docker hub, then add it to the lab orchestrator like this:

~~~{#lst:curladddocker .bash .long caption="add a docker image with curl"}
curl -u \
    admin:changeme \
    -X POST \
    -d name=ubuntu-cloud-gnome \
    -d description="Ubuntu cloud image with Gnome installed" \
    -d urls="USERNAME/REPO:VERSION" \
    localhost:5000/docker_image
~~~

**Add lab**

First you need to create a docker image and get its id. This can be done with `curl localhost:5000/docker_image`. After that you can create a lab like this:

~~~{#lst:curlcreatelab .bash .long caption="create lab with curl"}
curl \
    -u admin:changeme \
    -X POST \
    -d name="Lab Ubuntu Hacking" \
    -d namespace_prefix="lab-ubuntu-hacking" \
    -d description="How to hack ubuntu" \
    -d docker_image_id=1 \
    -d docker_image_name="ubuntu-cloud-gnome" \
    localhost:5000/lab
~~~

**Start a lab**

Start a lab instance:

~~~{#lst:curlstartlab .bash .long caption="start a lab instance with curl"}
curl \
    -u me:secret \
    -X POST \
    -d lab_id=1 \
    localhost:5000/lab_instance
~~~

Show the VMIs:

~~~{#lst:curlgetvmi .bash .long caption="list the VMIs with curl"}
curl \
    -u me:secret \
    localhost:5000/lab_instance/1/virtual_machine_instances/
~~~

Open noVNC

~~~{#lst:novncurlfinal .long caption="final URL for noVNC"}
http://localhost:8000/vnc_lite.html
    ?host=localhost
    &port=5001
    &path=LAB_INSTANCE_ID/TOKEN
~~~
