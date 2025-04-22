import logging
import time

import numpy as np

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

    def notify(self, sender, message, **kwargs):
        """Notifies all components with the message."""
        match message:
            case 'Scan':
                try:
                    scan_points = kwargs['scan_points']
                    acq_time = kwargs['acq_time']
                except KeyError:
                    raise AttributeError(f'No scan point or acquisition time is specified')

                self.scan(sender, scan_points, acq_time)

    def scan(self, sender, scan_points, acq_time):
        scan_motor = sender

        # first create new scan in data collector
        all_device_info = dict(device.get_device_info() for device in (self.sensors + self.controllers))
        scan_info = {'scan_points': len(scan_points), 'all_device_info': all_device_info}
        self.notify_data_managers('new_scan', scan_info)

        # Prepare console logging TODO: move to a dedicated DataComponent
        start_time = time.time()
        LOGGER.info("Scan starts...\n")
        idx_col_width = 5
        pos_col_width = 8
        time_col_width = 7
        count_col_width = 10
        LOGGER.info(f"| {'#':>{idx_col_width}} | {'pos':>{pos_col_width}} | {'time':>{time_col_width}} "
                    f"| {'count tot.':>{count_col_width}} |")
        LOGGER.info(
            f"| {'-' * idx_col_width} | {'-' * pos_col_width} | {'-' * time_col_width} | {'-' * count_col_width} |")

        spectra = []
        for (idx, position) in enumerate(scan_points):
            try:
                scan_motor.amove(position)
            except RuntimeError as exc:  # TODO: change to MotorNotReady error once available
                LOGGER.error(
                    "Scan interrupted at position %.2f", position)
                raise RuntimeError(f"Scan interrupted at position {position}") from exc

            # get_all_sensors data (acq_time)
            data = {}
            log_counts = np.nan
            if self.sensors:
                assert acq_time >= 0.
                for sensor in self.sensors:
                    # TODO: make asynchronous in case there are many sensors
                    data[sensor.alias] = sensor.acquisition(acquisition_time=acq_time)
                    log_counts = data[sensor.alias].counts.sum()
            elif acq_time > 0:
                time.sleep(acq_time)

            # Get all controller position
            positions = {ctlr.motor_name: ctlr.user_position for ctlr in self.controllers}

            point_data = {'idx': idx, 'data': data, 'positions': positions}
            self.notify_data_managers('new_scan_point', point_data)

            LOGGER.info(f"| {idx:{idx_col_width}.0f} | {position:{pos_col_width}.4f} "
                        f"| {acq_time:{time_col_width}.2f} | {log_counts:{count_col_width}.0f} |")

        self.notify_data_managers('close_scan', {})

        LOGGER.info(f"\n   Scan ended succesfully. Total duration was: {time.time() - start_time:.2f} s\n")

    def notify_data_managers(self, message, kwargs):
        for component in self.data_managers:
            LOGGER.debug(f'Notifying {component}...')
            component.receive(message, **kwargs)
