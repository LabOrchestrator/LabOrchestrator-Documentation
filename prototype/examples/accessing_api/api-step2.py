from flask import Flask, make_response, request
import requests
import os
import logging
import yaml
import re

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
        if self.insecure_ssl:
            verify = False
        elif self.cacert is None:
            verify = True
        else:
            verify = self.cacert
        response = requests.get(base_uri + address, headers=headers, verify=verify)
        return response.text

    def get_vmis(self, namespace=None):
        if namespace is None:
            namespace = "default"
        address = f"/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/"
        return self.get(address)

    def post(self, address, data):
        base_uri = f"https://{self.service_host}:{self.service_port}"
        headers = {"Authorization": f"Bearer {self.service_account_token}",
                   "Content-Type": "application/yaml"}
        if self.insecure_ssl:
            verify = False
        elif self.cacert is None:
            verify = True
        else:
            verify = self.cacert
        response = requests.post(base_uri + address, data=data, headers=headers, verify=verify)
        return response.text

    def create_vmi(self, data, namespace=None):
        if namespace is None:
            namespace = "default"
        address = f"/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/"
        return self.post(address, data)

    def delete(self, address):
        base_uri = f"https://{self.service_host}:{self.service_port}"
        headers = {"Authorization": f"Bearer {self.service_account_token}"}
        if self.insecure_ssl:
            verify = False
        elif self.cacert is None:
            verify = True
        else:
            verify = self.cacert
        response = requests.delete(base_uri + address, headers=headers, verify=verify)
        return response.text

    def delete_vmi(self, vmi_name, namespace=None):
        if namespace is None:
            namespace = "default"
        address = f"/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/{vmi_name}"
        return self.delete(address)


def create_kubernetes_api_default():
    kubernetes_service_host = os.environ["KUBERNETES_SERVICE_HOST"]
    kubernetes_service_port = os.environ["KUBERNETES_SERVICE_PORT"]
    service_account_token = None
    with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as reader:
        service_account_token = reader.read()
    cacert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
    k8s_api = KubernetesAPI(kubernetes_service_host, kubernetes_service_port,
                            service_account_token, cacert)
    return k8s_api


kubernetes_api = create_kubernetes_api_default()


class TemplateEngine:
    def __init__(self, data):
        self.path_matcher = re.compile(r'\$\{([^}^{]+)\}')
        self.data = data

    def path_constructor(self, loader, node):
        value = node.value
        match = self.path_matcher.match(value)
        var = match.group()[2:-1]
        val = self.data.get(var)
        # needed to prevent converting integers to strings
        if value[match.end():] == "":
            return val
        else:
            return str(val) + value[match.end():]

    def load_yaml(self, filename):
        yaml.add_implicit_resolver('!path', self.path_matcher)
        yaml.add_constructor('!path', self.path_constructor)

        cont = open(filename)
        p = yaml.load(cont, Loader=yaml.FullLoader)
        return p

    def replace(self, filename):
        y = self.load_yaml(filename)
        return yaml.dump(y, Dumper=yaml.Dumper)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/vmis")
def get_vmis():
    r = kubernetes_api.get_vmis()
    ret = make_response(r)
    ret.mimetype = 'application/json'
    return ret


@app.route("/create_vmi")
def create_vmi():
    vm_image = request.args.get('vm_image', type=str)
    vmi_name = request.args.get('vmi_name', type=str)
    namespace = "default"
    template_data = {"cores": 3, "memory": "3G",
                     "vm_image": vm_image, "vmi_name": vmi_name,
                     "namespace": namespace}
    template_engine = TemplateEngine(template_data)
    data = template_engine.replace('vmi_template.yaml')
    r = kubernetes_api.create_vmi(data, namespace)
    ret = make_response(r)
    ret.mimetype = 'application/json'
    return ret


@app.route("/delete_vmi")
def delete_vmi():
    vmi_name = request.args.get('vmi_name', type=str)
    namespace = "default"
    r = kubernetes_api.delete_vmi(vmi_name, namespace)
    ret = make_response(r)
    ret.mimetype = 'application/json'
    return ret

app.run(host='0.0.0.0', debug=True)
