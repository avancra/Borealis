import logging
from abc import ABCMeta, abstractmethod

from borealis import session_orchestrator
from borealis.data_structures import H5DataSchemas
from borealis.data_templates import MoverPositions

LOGGER = logging.getLogger(__name__)


class Component(metaclass=ABCMeta):
    """Base component class."""

    def __init__(self):
        self._orchestrator = session_orchestrator

    def send(self, message, **kwargs):
        """Sends a message to the mediator."""
        LOGGER.debug('Sending message: %s', message)
        self._orchestrator.dispatch(sender=self, message=message, **kwargs)

    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""


class DataComponent(Component, metaclass=ABCMeta):
    """Base data component class."""

    def __init__(self):
        super().__init__()
        self._orchestrator.add_data_component(self)


class DeviceComponent(Component, metaclass=ABCMeta):
    @abstractmethod
    def get_h5_data_schema(self) -> H5DataSchemas:
        """
        Must return a H5DataSchemas object containing:
            - alias: str  unique identifier for this component
            - attributes: dict
            - datasets: SchemaCollection

        """


class SensorComponent(DeviceComponent, metaclass=ABCMeta):
    """Base sensor component class."""

    def __init__(self):
        super().__init__()
        self._orchestrator.add_sensor_component(self)


class ControllerComponent(DeviceComponent, metaclass=ABCMeta):
    """Base controller component class."""

    def __init__(self):
        super().__init__()
        self._orchestrator.add_controller_component(self)

    @abstractmethod
    def get_position(self) -> MoverPositions:
        """ABC method to get device position as MoverPositions object."""