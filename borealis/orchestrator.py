import logging

LOGGER = logging.getLogger(__name__)


class Orchestrator():
    """Session orchestrator, keeps track of components and manages communication between them."""

    def __init__(self):
        self.sensors = []
        self.controllers = []
        self.data_managers = []

    def add_controller_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding controller component %s', component)
        try:
            assert hasattr(component, 'get_device_info')
        except AssertionError:
            LOGGER.error('Component %s is missing a get_device_info method', component)
            raise AttributeError(f'Component {component} has no get_device_info method')
        self.controllers.append(component)

    def add_sensor_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding sensor component %s', component)
        try:
            assert hasattr(component, 'get_device_info')
        except AssertionError:
            LOGGER.error('Component %s is missing a get_device_info method', component)
            raise AttributeError(f'Component {component} has no get_device_info method')
        self.sensors.append(component)

    def add_data_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding data manager %s', component)
        self.data_managers.append(component)

    def _remove_all_sensors(self):
        self.sensors = []

    def _remove_all_controllers(self):
        self.controllers = []

    def notify(self, sender, topic, message, **kwargs):
        """Notifies all components with the message."""
        # TODO: deal with dispatching logic here
        match topic:
            case 'DataPoint':
                # TODO: collect data from all sensors
                # TODO: collect status from all controllers
                self.notify_data_managers(sender, message, kwargs)
            case 'Scan':
                all_device_info = dict(device.get_device_info() for device in (self.sensors + self.controllers))
                assert 'all_device_info' not in kwargs
                kwargs['all_device_info'] = all_device_info
                self.notify_data_managers(sender, message, kwargs)

    def notify_data_managers(self, sender, message, kwargs):
        for component in self.data_managers:
            LOGGER.debug(f'Notifying {component}...')
            component.receive(message, **kwargs)






