from distutils.util import strtobool
import os
import logging

from lab_orchestrator_prototype.kubernetes.api import Proxy, APIRegistry
from lab_orchestrator_prototype.kubernetes.controller import NamespaceController, NetworkPolicyController, \
    DockerImageController, VirtualMachineInstanceController, LabController, LabInstanceController, ControllerCollection
from lab_orchestrator_prototype.routes import load_routes
from lab_orchestrator_prototype.user_management import create_admin
from lab_orchestrator_prototype.ws_proxy import WebsocketProxy
from lab_orchestrator_prototype.app import app, db, CC


def create_kubernetes_api_default() -> APIRegistry:
    if not app.config['local_dev_mode']:
        service_account_token = open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') .read()
        cacert = '/var/run/secrets/kubernetes.io/serviceaccount/ca.crt'
        protocol = "https"
    else:
        service_account_token = None
        cacert = None
        protocol = "http"
    kubernetes_service_host = app.config["kubernetes_service_host"]
    kubernetes_service_port = app.config["kubernetes_service_port"]
    base_uri = f"{protocol}://{kubernetes_service_host}:{kubernetes_service_port}"
    proxy = Proxy(base_uri, service_account_token, cacert)
    k8s_registry = APIRegistry(proxy)
    return k8s_registry


def create_cc(api_registry: APIRegistry) -> ControllerCollection:
    namespace_ctrl: NamespaceController = NamespaceController(api_registry)
    network_policy_ctrl: NetworkPolicyController = NetworkPolicyController(api_registry)
    docker_image_ctrl: DockerImageController = DockerImageController()
    virtual_machine_instance_ctrl: VirtualMachineInstanceController = VirtualMachineInstanceController(
        registry=api_registry,
        namespace_ctrl=namespace_ctrl,
        docker_image_ctrl=docker_image_ctrl
    )
    lab_ctrl: LabController = LabController()
    lab_instance_ctrl: LabInstanceController = LabInstanceController(
        virtual_machine_instance_ctrl=virtual_machine_instance_ctrl,
        namespace_ctrl=namespace_ctrl,
        lab_ctrl=lab_ctrl,
        network_policy_ctrl=network_policy_ctrl
    )
    return ControllerCollection(
        namespace_ctrl=namespace_ctrl,
        network_policy_ctrl=network_policy_ctrl,
        docker_image_ctrl=docker_image_ctrl,
        virtual_machine_instance_ctrl=virtual_machine_instance_ctrl,
        lab_ctrl=lab_ctrl,
        lab_instance_ctrl=lab_instance_ctrl
    )


##########
# CONFIG #
##########

def load_config():
    # local dev mode disables reading the kubernetes service
    # account files and assumes you are running kubectl proxy
    app.config.update(
        local_dev_mode=bool(strtobool(os.environ.get("LOCAL_DEV_MODE", "False"))),
        websocket_api_path="/apis/subresources.kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/{vmi_name}/vnc",
        ws_proxy_host=os.environ.get("WS_PROXY_HOST", "0.0.0.0"),
        ws_proxy_port=int(os.environ.get("WS_PROXY_PORT", "5001")),
        flask_run_host=os.environ.get("FLASK_RUN_HOST", "0.0.0.0"),
        flask_run_port=int(os.environ.get("FLASK_RUN_PORT", "5000")),
        kubernetes_service_host=os.environ["KUBERNETES_SERVICE_HOST"],
        kubernetes_service_port=os.environ["KUBERNETES_SERVICE_PORT"],
        admin_username=os.environ.get("ADMIN_USERNAME", "admin"),
        admin_password=os.environ.get("ADMIN_PASSWORD", "changeme")
    )
    if app.config["local_dev_mode"]:
        # local dev mode
        app.config['websocket_remote_url'] = os.environ.get("WS_REMOTE_URL", "ws://localhost:8001")
    else:
        # kubernetes mode
        kubernetes_service_host = app.config['kubernetes_service_host']
        kubernetes_service_port = app.config['kubernetes_service_port']
        app.config["websocket_remote_url"] = f"wss://{kubernetes_service_host}:{kubernetes_service_port}"


def run():
    # start websocket proxy
    wp = WebsocketProxy(app.config["websocket_remote_url"], app.config["websocket_api_path"], app.config["local_dev_mode"])
    wp.run_in_thread(app.config["ws_proxy_host"], app.config["ws_proxy_port"])
    # start api
    app.run(host=app.config["flask_run_host"], port=app.config["flask_run_port"], debug=False)
    # stop after api has stopped
    wp.stop_thread()
    logging.info("Shutdown complete")


def main():
    # load config
    load_config()
    load_routes()
    # create global objects
    api_registry: APIRegistry = create_kubernetes_api_default()
    CC.set(create_cc(api_registry))
    # create database
    if not os.path.exists('db.sqlite'):
        db.create_all()
    create_admin(app.config['admin_username'], app.config['admin_password'])
    run()
