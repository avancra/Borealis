
import borealis as b

offset= {
    "det_y":666,
    "det_y":12,
}

corr = {
    "det_y":[1,2,3],
    "det_y":[4,5,6]
}


det = b.amptek.AmptekCdTe123(...)
det_y = b.motor.Motor(chan=2, offset=offset["det_y"])
...

spectro = {
    "det_y" : det_y,
    "-...": ...,
    "src_y"
}

class RevTheta(b.pseudo_motor.Theta):

    def get_src_x(theta):
        return cos*sin 

    def get_src_y(theta):
        return ...
    
    def get_src_pos(theta):
        return pos_y, pos_x

    @staticmethod
    def torad(theta):
        return pi*theta/180


theta = RevTheta(spectro, radius=500)


energy = b.pseudo_motor.Energy(theta, d_hkl=2.4)

_____________________________

pseudo_motor.py 

class Theta(ABC):

    def __init__(self, radius):
        self.radius = radius
        self._det_y = spectro['det_y'] if 'det_y' in spectro else None
        self._src_y = spectro['src_y'] if 'src_y' in spectro else None
        ...

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
        


________________________

$ conda activate borealis (pip install borealis)
$ python -m borealis revontuli.py
>>> det.start_acquisition(10)
>>> det_y.mvabs(456)
>>> det_y.mvrel(2)
>>> theta.mvabs(82.5)
>>> theta.scan(66, 88, 2)
>>> energy.scan(12, 17, 0.5)
>>> energy.mvrel(0.5)
>>> energy.mvabs(16,66)
>>> exit()