import logging
from abc import ABC
from typing import Dict, Type, Callable, Union, Optional

import requests

API_EXTENSIONS_NAMESPACED: Dict[str, Type['NamespacedApi']] = {}
API_EXTENSIONS_NOT_NAMESPACED: Dict[str, Type['NotNamespacedApi']] = {}


def add_api_namespaced(name: str) -> Callable[[Type['NamespacedApi'],], Type['NamespacedApi']]:
    def inner(cls: Type[NamespacedApi]) -> Type[NamespacedApi]:
        API_EXTENSIONS_NAMESPACED[name] = cls
        return cls
    return inner


def add_api_not_namespaced(name: str) -> Callable[[Type['NotNamespacedApi'],], Type['NotNamespacedApi']]:
    def inner(cls: Type[NotNamespacedApi]) -> Type[NotNamespacedApi]:
        API_EXTENSIONS_NOT_NAMESPACED[name] = cls
        return cls
    return inner


class Proxy:
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
        response = requests.get(self.base_uri + address,
                                headers=headers, verify=self.verify)
        return response.text

    def post(self, address, data):
        headers = {"Authorization": f"Bearer {self.service_account_token}",
                   "Content-Type": "application/yaml"}
        response = requests.post(self.base_uri + address,
                                 data=data, headers=headers, verify=self.verify)
        return response.text

    def delete(self, address):
        headers = {"Authorization": f"Bearer {self.service_account_token}"}
        response = requests.delete(self.base_uri + address,
                                   headers=headers, verify=self.verify)
        return response.text


class APIRegistry:
    def __init__(self, proxy: Proxy):
        self.proxy = proxy

    def __getattr__(self, name) -> Union['NamespacedApi', 'NotNamespacedApi']:
        cls: Union[Optional[Type['NamespacedApi']], Optional[Type['NotNamespacedApi']]]
        if cls := API_EXTENSIONS_NAMESPACED.get(name):
            return cls(self.proxy)
        if cls := API_EXTENSIONS_NOT_NAMESPACED.get(name):
            return cls(self.proxy)
        raise AttributeError(f'{name} not found')


class ApiExtension(ABC):
    list_url = None
    detail_url = None

    def __init__(self, proxy: Proxy):
        self.proxy = proxy


class NamespacedApi(ApiExtension):
    def get_list(self, namespace):
        return self.proxy.get(self.list_url.format(namespace=namespace))

    def create(self, namespace, data):
        return self.proxy.post(self.list_url.format(namespace=namespace), data)

    def get(self, namespace, identifier):
        return self.proxy.get(self.detail_url.format(namespace=namespace, identifier=identifier))

    def delete(self, namespace, identifier):
        return self.proxy.delete(self.detail_url.format(namespace=namespace, identifier=identifier))


class NotNamespacedApi(ApiExtension):
    def get_list(self):
        return self.proxy.get(self.list_url)

    def create(self, data):
        return self.proxy.post(self.list_url, data)

    def get(self, identifier):
        return self.proxy.get(self.detail_url.format(identifier=identifier))

    def delete(self, identifier):
        return self.proxy.delete(self.detail_url.format(identifier=identifier))


@add_api_not_namespaced("namespace")
class Namespace(NotNamespacedApi):
    list_url = "/api/v1/namespaces"
    detail_url = "/api/v1/namespaces/{identifier}"


@add_api_namespaced("virtual_machine_instance")
class VirtualMachineInstance(NamespacedApi):
    list_url = "/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/"
    detail_url = "/apis/kubevirt.io/v1alpha3/namespaces/{namespace}/virtualmachineinstances/{identifier}"


@add_api_namespaced("network_policy")
class NetworkPolicy(NamespacedApi):
    list_url = "/apis/networking.k8s.io/v1/namespaces/{namespace}/networkpolicies"
    detail_url = "/apis/networking.k8s.io/v1/namespaces/{namespace}/networkpolicies/{identifier}"
