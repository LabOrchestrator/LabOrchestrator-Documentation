from abc import ABC
from dataclasses import dataclass
from typing import Type, Union, List

from flask import make_response, jsonify

from lab_orchestrator_prototype.app import db
from lab_orchestrator_prototype.kubernetes.api import APIRegistry, NamespacedApi, NotNamespacedApi
from lab_orchestrator_prototype.model import DockerImage, Lab, LabInstance
from lab_orchestrator_prototype.template_engine import TemplateEngine
from lab_orchestrator_prototype.user_management import User


class ModelController(ABC):
    def _model(self) -> Type[db.Model]:
        raise NotImplementedError()

    def get_list(self):
        return self._model().query.all()

    def _create(self, *args, **kwargs) -> db.Model:
        obj = self._model()(*args, **kwargs)
        db.session.add(obj)
        db.session.commit()
        return obj

    def get(self, id) -> db.Model:
        obj = self._model().query.get(id)
        if obj is None:
            raise KeyError(f"Key error: {id}")
        return obj

    def delete(self, obj: db.Model):
        db.session.delete(obj)
        db.session.commit()

    def _serialize(self, obj):
        raise NotImplementedError()

    def make_response(self, inp: Union[db.Model, List[db.Model]]):
        if isinstance(inp, list):
            return jsonify([self._serialize(obj) for obj in inp])
        return jsonify(self._serialize(inp))


class KubernetesController(ABC):
    template_file = None

    def __init__(self, registry: APIRegistry):
        self.registry = registry

    def _get_template(self, template_data):
        template_engine = TemplateEngine(template_data)
        return template_engine.replace(self.template_file)

    def make_response(self, inp: Union[db.Model, List[db.Model]]):
        ret = make_response(inp)
        ret.mimetype = 'application/json'
        return ret


class NamespacedController(KubernetesController):
    def _api(self) -> NamespacedApi:
        raise NotImplementedError()

    def get_list(self, namespace):
        return self._api().get_list(namespace)

    def get(self, namespace, identifier):
        return self._api().get(namespace, identifier)

    def delete(self, namespace, identifier):
        return self._api().delete(namespace, identifier)


class NotNamespacedController(KubernetesController):
    def _api(self) -> NotNamespacedApi:
        raise NotImplementedError()

    def get_list(self):
        return self._api().get_list()

    def get(self, identifier):
        return self._api().get(identifier)

    def delete(self, identifier):
        return self._api().delete(identifier)


class NamespaceController(NotNamespacedController):
    template_file = 'templates/namespace_template.yaml'

    def _api(self) -> NotNamespacedApi:
        return self.registry.namespace

    def create(self, namespace):
        template_data = {'namespace': namespace}
        data = self._get_template(template_data)
        return self._api().create(data)


class NetworkPolicyController(NamespacedController):
    template_file = 'templates/network_policy_template.yaml'

    def _api(self) -> NamespacedApi:
        return self.registry.network_policy

    def __init__(self, registry: APIRegistry):
        super().__init__(registry)
        self.default_name = "allow-same-namespace"

    def create(self, namespace):
        template_data = {'namespace': namespace, 'network_policy_name': self.default_name}
        data = self._get_template(template_data)
        return self._api().create(namespace, data)


class DockerImageController(ModelController):
    def _model(self) -> Type[db.Model]:
        return DockerImage

    def _serialize(self, obj):
        return {'id': obj.id, 'name': obj.name, 'description': obj.description, 'urls': obj.urls}

    def create(self, name, description, urls):
        return self._create(name=name, description=description, urls=urls)


class VirtualMachineInstanceController(NamespacedController):
    template_file = 'templates/vmi_template.yaml'

    def __init__(self, registry: APIRegistry, namespace_ctrl: NamespaceController,
                 docker_image_ctrl: DockerImageController):
        super().__init__(registry)
        self.namespace_ctrl = namespace_ctrl
        self.docker_image_ctrl = docker_image_ctrl

    def _api(self) -> NamespacedApi:
        return self.registry.virtual_machine_instance

    def create(self, namespace, lab: Lab):
        docker_image = self.docker_image_ctrl.get(lab.docker_image)
        template_data = {"cores": 3, "memory": "3G",
                         "vm_image": docker_image.urls, "vmi_name": lab.docker_image_name,
                         "namespace": namespace}
        data = self._get_template(template_data)
        return self._api().create(namespace, data)

    def get_list_of_lab_instance(self, lab_instance: LabInstance):
        namespace_name = LabInstanceController.get_namespace_name(lab_instance)
        namespace = self.namespace_ctrl.get(namespace_name)
        return self.get_list(namespace_name)

    def get_of_lab_instance(self, lab_instance: LabInstance, virtual_machine_instance_id):
        namespace_name = LabInstanceController.get_namespace_name(lab_instance)
        namespace = self.namespace_ctrl.get(namespace_name)
        return self.get(namespace_name, virtual_machine_instance_id)


class LabController(ModelController):
    def _model(self) -> Type[db.Model]:
        return Lab

    def _serialize(self, obj):
        return {'id': obj.id, 'name': obj.name, 'namespace_prefix': obj.namespace_prefix,
                'description': obj.description, 'docker_image': obj.docker_image,
                'docker_image_name': obj.docker_image_name}

    def create(self, name, namespace_prefix, description, docker_image: DockerImage, docker_image_name) -> db.Model:
        return self._create(name=name, namespace_prefix=namespace_prefix, description=description,
                            docker_image=docker_image.id, docker_image_name=docker_image_name)


class LabInstanceController(ModelController):
    def _model(self) -> Type[db.Model]:
        return LabInstance

    def _serialize(self, obj):
        return {'id': obj.id, 'lab_id': obj.lab_id, 'user_id': obj.user_id}

    def __init__(self, virtual_machine_instance_ctrl: VirtualMachineInstanceController,
                 namespace_ctrl: NamespaceController, lab_ctrl: LabController,
                 network_policy_ctrl: NetworkPolicyController):
        super().__init__()
        self.virtual_machine_instance_ctrl = virtual_machine_instance_ctrl
        self.namespace_ctrl = namespace_ctrl
        self.lab_ctrl = lab_ctrl
        self.network_policy_ctrl = network_policy_ctrl

    @staticmethod
    def get_namespace_name(lab_instance: LabInstance):
        lab = Lab.query.get(lab_instance.lab_id)
        return LabInstanceController.gen_namespace_name(lab, lab_instance.user_id, lab_instance.id)

    @staticmethod
    def gen_namespace_name(lab: Lab, user_id, lab_instance_id):
        return f"{lab.namespace_prefix}-{user_id}-{lab_instance_id}"

    def create(self, lab: Lab, user: User):
        lab_instance = self._create(lab_id=lab.id, user_id=user.id)
        # create namespace
        namespace_name = LabInstanceController.gen_namespace_name(lab, user.id, lab_instance.id)
        namespace = self.namespace_ctrl.create(namespace_name)
        # create network policy
        network_policy = self.network_policy_ctrl.create(namespace_name)
        # create vmi
        vmi = self.virtual_machine_instance_ctrl.create(namespace_name, lab)
        return lab_instance

    def delete(self, lab_instance: LabInstance):
        super().delete(lab_instance)
        lab = self.lab_ctrl.get(lab_instance.lab_id)
        namespace_name = LabInstanceController.gen_namespace_name(lab, lab_instance.user_id, lab_instance.id)
        self.namespace_ctrl.delete(namespace_name)
        # this also deletes VMIs and all other resources in the namespace

    def get_list_of_user(self, user: User):
        lab_instances = LabInstance.query.filter_by(user_id=user.id).all()
        return lab_instances


@dataclass
class ControllerCollection:
    namespace_ctrl: NamespaceController
    network_policy_ctrl: NetworkPolicyController
    docker_image_ctrl: DockerImageController
    virtual_machine_instance_ctrl: VirtualMachineInstanceController
    lab_ctrl: LabController
    lab_instance_ctrl: LabInstanceController