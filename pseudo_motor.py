from abc import ABC, abstractmethod, abstractproperty


class Theta(ABC):

    def __init__(self, radius, spectro_cmpt):
        """Provide pseudo motor to perform angle."""
        self.radius = radius
        self._det_y = spectro_cmpt['det_y'] if 'det_y' in spectro_cmpt else None
        self._src_y = spectro_cmpt['src_y'] if 'src_y' in spectro_cmpt else None
        ...
1
    def mvabs(pos):
        if self._det_y is not None:
            self.det_y.move(self.get_src_x(pos))
        if self._src_x is not None:
            self.det_y.move(self.get_src_x(pos))
        ...

    def scan(start, stop, step):
        for pos in range(start, stop, step):
            self.mvabs(pos)

    def get_src_x(pos):
        return 0

    @staticmethod
    def torad(theta):
        return pi*theta/180