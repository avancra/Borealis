import logging

LOGGER = logging.getLogger(__name__)


class Orchestrator():
    """Session orchestrator, keep track of components and manages communication between them."""

    def __init__(self):
        self.sensor_components = []
        self.controller_components = []
        self.data_managers = []

    def add_controller_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding controller component %s', component)
        self.controller_components.append(component)

    def add_sensor_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding sensor component %s', component)
        self.sensor_components.append(component)

    def add_data_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding data manager %s', component)
        self.data_managers.append(component)

    def notify(self, sender, topic, message, **kwargs):
        """Notifies all components with the message."""
        # TODO: deal with dispatching logic here
        match topic:
            case 'DataPoint':
                self.notify_data_managers(sender, message, kwargs)
            case 'Scan':
                self.notify_data_managers(sender, message, kwargs)

    def notify_data_managers(self, sender, message, kwargs):
        for component in self.data_managers:
            LOGGER.debug(f'Notifying {component}...')
            component.receive(message, **kwargs)





