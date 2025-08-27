import logging
from abc import ABCMeta, abstractmethod

LOGGER = logging.getLogger(__name__)


class Component(metaclass=ABCMeta):
    """Base component class."""

    def __init__(self, session_orchestrator):
        self._orchestrator = session_orchestrator

    def send(self, message, **kwargs):
        """Sends a message to the mediator."""
        LOGGER.debug('Sending message: %s', message)
        self._orchestrator.notify(sender=self, message=message, **kwargs)

    @abstractmethod
    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""


class SensorComponent(Component):
    """Base sensor component class."""

    def __init__(self, session_orchestrator):
        super().__init__(session_orchestrator)
        self._orchestrator.add_sensor_component(self)

    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""


class DataComponent(Component):
    """Base data component class."""

    def __init__(self, session_orchestrator):
        super().__init__(session_orchestrator)
        self._orchestrator.add_data_component(self)

    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""


class ControllerComponent(Component):
    """Base controller component class."""

    def __init__(self, session_orchestrator):
        super().__init__(session_orchestrator)
        self._orchestrator.add_controller_component(self)

    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""
