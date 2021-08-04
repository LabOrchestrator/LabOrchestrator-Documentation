from flask import Flask, make_response, request
from distutils.util import strtobool
import requests
import os
import logging

from template_engine import TemplateEngine
from ws_proxy import WebsocketProxy, add_token

app = Flask(__name__)


class KubernetesAPI:
    def __init__(self, base_uri, service_account_token=None,
                 cacert=None, insecure_ssl=False):
        if service_account_token is None:
            logging.warning("No service account token.")
        if cacert is None:
            logging.warning("No cacert.")
        self.base_uri = base_uri
        self.service_account_token = service_account_token
        if insecure_ssl:
            self.verify = False
        elif cacert is None:
            self.verify = True
        else:
            self.verify = cacert

    def get(self, address):
        headers = {"Authorization": f"Bearer {self.service_account_token}"}
        response = requests.get(self.base_uri + address, headers=headers, verify=self.verify)
        return response.text

    def get_vmis(self, namespace=None):
        if namespace is None:
            namespace = "default"
        address = f"/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/"
        return self.get(address)

    def post(self, address, data):
        headers = {"Authorization": f"Bearer {self.service_account_token}",
                   "Content-Type": "application/yaml"}
        response = requests.post(self.base_uri + address, data=data, headers=headers, verify=self.verify)
        return response.text

    def create_vmi(self, data, namespace=None):
        if namespace is None:
            namespace = "default"
        address = f"/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/"
        return self.post(address, data)

    def delete(self, address):
        headers = {"Authorization": f"Bearer {self.service_account_token}"}
        response = requests.delete(self.base_uri + address, headers=headers, verify=self.verify)
        return response.text

    def delete_vmi(self, vmi_name, namespace=None):
        if namespace is None:
            namespace = "default"
        address = f"/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/{vmi_name}"
        return self.delete(address)


def create_kubernetes_api_default(local_dev_mode: False):
    kubernetes_service_host = os.environ["KUBERNETES_SERVICE_HOST"]
    kubernetes_service_port = os.environ["KUBERNETES_SERVICE_PORT"]
    cacert = None
    service_account_token = None
    if not local_dev_mode:
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as reader:
            service_account_token = reader.read()
        cacert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
        base_uri = f"https://{kubernetes_service_host}:{kubernetes_service_port}"
    else:
        base_uri = f"http://{kubernetes_service_host}:{kubernetes_service_port}"
    k8s_api = KubernetesAPI(base_uri, service_account_token, cacert)
    return k8s_api


KUBERNETES_API = None


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/vmis")
def get_vmis():
    r = KUBERNETES_API.get_vmis()
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
    r = KUBERNETES_API.create_vmi(data, namespace)
    ret = make_response(r)
    ret.mimetype = 'application/json'
    return ret


@app.route("/delete_vmi")
def delete_vmi():
    vmi_name = request.args.get('vmi_name', type=str)
    namespace = "default"
    r = KUBERNETES_API.delete_vmi(vmi_name, namespace)
    ret = make_response(r)
    ret.mimetype = 'application/json'
    return ret


@app.route("/add_credentials")
def add_credentials():
    user = request.args.get('user', type=str)
    token = request.args.get('token', type=str)
    vmi_name = request.args.get('vmi_name', type=str)
    valid = add_token(token, user, vmi_name)
    if valid:
        return "Added credentials."
    else:
        return "Adding credentials not possible.", 400


conf = {
    "websocket_remote_url": "ws://localhost:8001",
    "websocket_api_path": "/apis/subresources.kubevirt.io/v1alpha3/namespaces/default/virtualmachineinstances/{path}/vnc",
    "ws_proxy_host": "0.0.0.0",
    "ws_proxy_port": 5001,
    "flask_host": "0.0.0.0",
    "flask_port": 5000,
}


def run(conf):
    wp = WebsocketProxy(conf["websocket_remote_url"], conf["websocket_api_path"])
    wp.run_in_thread(conf["ws_proxy_host"], conf["ws_proxy_port"])
    app.run(host=conf["flask_host"], port=conf["flask_port"], debug=False)
    wp.stop_thread()
    logging.info("Shutdown complete")


def main():
    # local dev mode disables reading the kubernetes service
    # account files and assumes you are running kubectl proxy
    local_dev_mode_str = os.environ.get("LOCAL_DEV_MODE", "False")
    local_dev_mode = bool(strtobool(local_dev_mode_str))
    if not local_dev_mode:
        kubernetes_service_host = os.environ["KUBERNETES_SERVICE_HOST"]
        kubernetes_service_port = os.environ["KUBERNETES_SERVICE_PORT"]
        conf["websocket_remote_url"] = kubernetes_service_host + ":" + str(kubernetes_service_port)
    KUBERNETES_API = create_kubernetes_api_default(local_dev_mode)
    run(conf)


if __name__ == '__main__':
    main()
