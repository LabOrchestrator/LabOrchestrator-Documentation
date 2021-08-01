from flask import Flask, make_response
import requests
import os
import logging

app = Flask(__name__)


class KubernetesAPI:
    def __init__(self, kubernetes_service_host, kubernetes_service_port,
                 service_account_token=None, cacert=None, insecure_ssl=False):
        if service_account_token is None:
            logging.warning("No service account token.")
        if cacert is None:
            logging.warning("No cacert.")
        self.service_host = kubernetes_service_host
        self.service_port = kubernetes_service_port
        self.service_account_token = service_account_token
        self.cacert = cacert
        self.insecure_ssl = insecure_ssl

    def get(self, address):
        base_uri = f"https://{self.service_host}:{self.service_port}"
        headers = {"Authorization": f"Bearer {self.service_account_token}"}
        response = requests.get(base_uri + address, headers=headers, verify=not self.insecure_ssl)
        return response.text

    def get_vmis(self, namespace=None):
        if namespace is None:
            namespace = "default"
        address = f"/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/"
        return self.get(address)


def create_kubernetes_api_default():
    kubernetes_service_host = os.environ["KUBERNETES_SERVICE_HOST"]
    kubernetes_service_port = os.environ["KUBERNETES_SERVICE_PORT"]
    service_account_token = None
    with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as reader:
        service_account_token = reader.read()
    cacert = None
    with open('/var/run/secrets/kubernetes.io/serviceaccount/ca.crt', 'r') as reader:
        cacert = reader.read()
    k8s_api = KubernetesAPI(kubernetes_service_host, kubernetes_service_port,
                            service_account_token, cacert)
    k8s_api.insecure_ssl = True
    return k8s_api


kubernetes_api = create_kubernetes_api_default()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/vmis")
def get_vmis():
    r = kubernetes_api.get_vmis()
    ret = make_response(r)
    ret.mimetype = 'application/json'
    return ret


app.run(host='0.0.0.0')
