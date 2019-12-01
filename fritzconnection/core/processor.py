"""
processor.py

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
"""

from .utils import localname


def process_node(obj, root):
    """
    Take an object and a root of nodes. The content of nodes with the
    same name as an instance-attribute of 'obj' are set as values for the
    corresponding instance-attribute. If the attribute is a callable,
    processing the node gets delegated to the callable (which in turn
    calls process_node).
    """
    for node in root:
        node_name = localname(node)
        try:
            attr = getattr(obj, node_name)
        except AttributeError:
            # ignore node
            continue
        if callable(attr):
            # delegate further processing to callable
            attr(node)
        else:
            # set attribute value
            setattr(obj, node_name, node.text.strip())


def processor(cls):
    """
    Class decorator to add the functionality calling 'process_node' if a
    class instance gets invoked as a callable.
    """
    cls.__call__ = lambda obj, root: process_node(obj, root)
    return cls


@processor
class SpecVersion:
    """
    Specification version from the schema device or service
    informations.
    """

    def __init__(self):
        self.major = None
        self.minor = None

    @property
    def version(self):
        return f'{self.major}.{self.minor}'


@processor
class Device:
    """
    Storage for devices attributes:
    """

    def __init__(self):
        self.deviceType = None
        self.friendlyName = None
        self.manufacturer = None
        self.manufacturerURL = None
        self.modelDescription = None
        self.modelName = None
        self.modelNumber = None
        self.modelURL = None
        self.UDN = None
        self.presentationURL = None

    @property
    def model_name(self):
        return self.modelName


class Description:
    """
    Root class for a given description information as the content from
    the files igddesc.xml or tr64desc.xml
    """

    def __init__(self, root):
        self._spec_version = None
        self._device = None
        process_node(self, root)

    @property
    def specVersion(self):
        if not self._spec_version:
            self._spec_version = SpecVersion()
        return self._spec_version

    # --- public api: ---------------------------
    @property
    def device(self):
        if not self._device:
            self._device = Device()
        return self._device

    @property
    def device_model_name(self):
        return self.device.model_name

    @property
    def spec_version(self):
        return self._spec_version.version
