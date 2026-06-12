# Adding a new detector type to Borealis

## Define a new module and class
1. Create new module in the `detector` package
2. inherit from `detector_base` in order to plug-in all the proper internals 
   from the Borealis library.
   
   ```python
   from borealis.detector.detector_base import Detector
   
   class MinipixTPX3(Detector):

       def __init__(self, alias: str = 'Minipix TPX3'):
           super().__init__(alias)
   ```
   
   Adding a default alias to the new class `__init__` function is optional but 
   highly recommended, as the alias is used in the logs and are by default 
   `Undefined` if no alias is provided by the user nor by the subclass `__init__` 
   function.

3. Override the mandatory methods as needed. 

## Add logging

The Borealis library implements logging, and new modules must also use the 
same mechanisms for consistency and ensuring the same format as the 
other log messages coming from Borealis.

Adding these 2 lines at import level of the module will initialise a `LOGGER` 
variable that can be used to log any message anywhere in this module using 
the logger configuration defined at library level.
```python
import logging

LOGGER = logging.getLogger(__name__)
```

Additionally, all classes inheriting from `Detector` get a `log()` method that 
automatically prepends the device's alias to the log message for easier 
debugging. It is recommended to make use of this method whenever it makes sense.
The intended use of this dedicated `log()` method is to identify the origin of 
the logged action, such as starting an acquisition. Example usage showing 
the difference between general `LOGGER` use and `cls.log()` use is shown in the 
`DummyDet` class.

