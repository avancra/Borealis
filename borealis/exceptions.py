

class BorealisException(Exception):

    pass


class SoftLimitError(BorealisException):

    def __init__(self, value, alias, limit_low, limit_high):
        message = (f'The dial position {value} for motor {alias.upper()} is outside the '
                   f'available soft limit range [{limit_low}:{limit_high}].')
        super().__init__(message)


class NotReadyError(BorealisException):

    def __init__(self, alias):
        message = (f'The device {alias.upper()} is not ready.')
        super().__init__(message)


class LimitSwitchError(BorealisException):

    def __init__(self, alias):
        message = (f'The limit switch for device {alias.upper()} is activated.')
        super().__init__(message)