import logging
from abc import ABCMeta, abstractmethod

from borealis import session_orchestrator
from borealis.data_structures import DeviceInfo

LOGGER = logging.getLogger(__name__)


class Component(metaclass=ABCMeta):
    """Base component class."""

    def __init__(self):
        self._orchestrator = session_orchestrator

    def send(self, message, **kwargs):
        """Sends a message to the mediator."""
        LOGGER.debug('Sending message: %s', message)
        self._orchestrator.notify(sender=self, message=message, **kwargs)

    @abstractmethod
    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""


class DeviceComponent(Component):
    @abstractmethod
    def get_device_info(self) -> DeviceInfo:
        """
        Must return a DeviceInfo object containing:
            - alias: unique identifier for this component
            - metadata: dictionary of device metadata
        """

class SensorComponent(DeviceComponent):
    """Base sensor component class."""

    def __init__(self):
        super().__init__()
        self._orchestrator.add_sensor_component(self)

    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""


class DataComponent(Component):
    """Base data component class."""

    def __init__(self):
        super().__init__()
        self._orchestrator.add_data_component(self)

    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""


class ControllerComponent(DeviceComponent):
    """Base controller component class."""

    def __init__(self):
        super().__init__()
        self._orchestrator.add_controller_component(self)

    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""
