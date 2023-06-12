import sys

sys.path.append("C:\\LocalData\\HotXAS")

from borealis.newport import NewportXPS
from borealis.motor import Motor 


### INITIALIZATION OF CONTROLER ####

_ctrler = NewportXPS()
_ctrler.initialise("192.168.2.4", 5001)


### INITIALIZATION OF MOTORS ####

tubex = Motor("X-ray tube translation along x", 'tubex', 0, _ctrler)
_ctrler._xps.GroupInitialize('tubex')
_ctrler._xps.GroupHomeSearch('tubex')