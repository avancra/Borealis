import logging
import time

import numpy as np

from borealis.data_structures import DeviceInfo

LOGGER = logging.getLogger(__name__)


class Orchestrator():
    """Session orchestrator, keeps track of components and manages communication between them."""

    def __init__(self):
        self.sensors = []
        self.controllers = []
        self.data_managers = []

    def add_data_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding data manager %s', component)
        self.data_managers.append(component)

    def add_controller_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding controller component %s', component)

        self._ensure_unique_alias(component)
        self._validate_device_info(component)
        self.controllers.append(component)

    def add_sensor_component(self, component):
        """Adds a component to the mediator."""
        LOGGER.debug('Adding sensor component %s', component)

        self._ensure_unique_alias(component)
        self._validate_device_info(component)
        self.sensors.append(component)

    def _ensure_unique_alias(self, component):
        all_aliases = [cpnt.alias for cpnt in (self.sensors + self.controllers)]
        if component.alias in all_aliases:
            raise ValueError(f"Duplicate alias detected: '{component.alias}'")

    @staticmethod
    def _validate_device_info(component):
        if not hasattr(component, "get_device_info"):
            LOGGER.error("Component %s is missing get_device_info()", component)
            raise AttributeError(f"Component {component} must implement get_device_info()")
        dev_info = component.get_device_info()
        if not isinstance(dev_info, DeviceInfo):
            LOGGER.error(
                "Component %s get_device_info() must return DeviceInfo, got %s",
                component, type(dev_info)
            )
            raise TypeError(
                f"{component} get_device_info() must return DeviceInfo, got {type(dev_info)}"
            )

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
                    acq_times = kwargs['acq_times']
                except KeyError:
                    raise AttributeError(f'No scan point or acquisition times is specified')

                self.scan(sender, scan_points, acq_times)

    def scan(self, sender, scan_points, acq_times):
        scan_motor = sender

        if len(scan_points) != len(acq_times):
            raise ValueError("Length of scan points and acquisition times does not match")

        # first create new scan in data collector
        all_device_info = {
            info.alias: info.metadata
            for info in (device.get_device_info() for device in (self.sensors + self.controllers))
        }
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

        for idx, (position, acq_time) in enumerate(zip(scan_points, acq_times)):
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
                time.sleep(float(acq_time))

            # Get all controller position
            positions = {ctlr.alias: ctlr.user_position for ctlr in self.controllers}

            point_data = {'idx': idx, 'data': data, 'positions': positions}
            self.notify_data_managers('new_scan_point', point_data)

            LOGGER.info(f"| {idx:{idx_col_width}.0f} | {position:{pos_col_width}.4f} "
                        f"| {acq_time:{time_col_width}.2f} | {log_counts:{count_col_width}.0f} |")

        self.notify_data_managers('close_scan', {})

        LOGGER.info(f"\n   Scan ended successfully. Total duration was: {time.time() - start_time:.2f} s\n")

    def notify_data_managers(self, message, kwargs):
        for component in self.data_managers:
            LOGGER.debug(f'Notifying {component}...')
            component.receive(message, **kwargs)
