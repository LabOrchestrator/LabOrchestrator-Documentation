\pagebreak

# Prototype

In this chapter we will abstract the concepts of the last chapter and include them in a prototype. The prototype will add additional concepts like authentication and multi-user support. The prototype should be used to deploy labs and should on the one hand prove that this project is feasible and on the other hand serve as a template for the alpha phase.

## Deploying an API to the cluster TODO

The prototype will have an API and will be deployed with Kubernetes.

## Using the Kubernetes API TODO

### Authorization

Creating a service account, RBAC und co

## Authorization, Multi-user support and Routing TODO
[KubeVirt Authorization](https://kubevirt.io/user-guide/operations/authorization/)^[https://kubevirt.io/user-guide/operations/authorization/]

Because Kubernetes can be accessed through an API, we can wrap all methods in an application and add authorization in a different layer. This will be shown in the prototype.

Hier wird nach einer Lösung gesucht, womit es möglich ist mehrere user zu haben und dass ein user nur auf sein lab zugreifen kann.

Hier werden die vnc und ttyd dienste, welche wir nutzen über ingresses oder services nach außen erreichbar gemacht. Für vnc werden wir vermutlich einen proxy bauen müssen oder ähnliches um die k8 api zu wrappen.

