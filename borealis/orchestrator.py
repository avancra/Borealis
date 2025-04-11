import logging
from abc import ABC, abstractmethod

LOGGER = logging.getLogger(__name__)


class Mediator(ABC):
    """Mediator interface declares communication methods."""
    @abstractmethod
    def notify(self, sender, message, **kwargs):
        """Notify method for sending messages to components."""
        pass


class Orchestrator(Mediator):
    """Concrete Mediator manages communication between components."""
    def __init__(self):
        self._components = []

    def add_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding component %s', component)
        self._components.append(component)

    def notify(self, sender, message, **kwargs):
        """Notifies all components with the message."""
        for component in self._components:
            if component is not sender:
                LOGGER.debug(f'Notifying... {component}')
                component.receive(message, **kwargs)




