

class BorealisException(Exception):

    pass


class SoftLimitError(BorealisException):

    def __init__(self, value: float, alias: str, limit_low: float, limit_high: float):
        message = (f'The dial position {value:.2f} for motor {alias.upper()} is outside the '
                   f'available soft limit range [{limit_low:.2f}:{limit_high:.2f}].')
        super().__init__(message)


class NotReadyError(BorealisException):

    def __init__(self, alias: str):
        message = (f'The device {alias.upper()} is not ready.')
        super().__init__(message)


class LimitSwitchError(BorealisException):

    def __init__(self, alias: str):
        message = (f'The limit switch for device {alias.upper()} is activated.')
        super().__init__(message)