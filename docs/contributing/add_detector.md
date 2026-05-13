# Adding a new detector type to Borealis

## Define a new module and class
1. Create new module in the `detector` package
2. inherit from detector_base in order to plug-in all the prper internals 
   from the Borealis library.
    ```python
    from borealis.detector.detector_base import Detector

    class MinipixTPX3(Detector):
    
        def __init__(self, alias: str = 'Minipix TPX3'):
            super().__init__(alias)
    ```
    Adding a default alias to the new class init function is optional but 
   highly recommended, as the alias is used in the logs and are by default 
   Undefined if no alias is provided by the user nor by the sub-class init 
   function.

   
3. Override the mandatory methods as needed. 

## Add logging

It is recomended to use the same logging mechanism already implemented in 
the Borealis library to get the logging output in the same format as the 
other log messages coming from Borealis.

Adding these 2 lines at import level of the module will initialise a `LOGGER` 
variable that can be used to log any message anywhere in this module using 
the logger configuration defined at library level.
```python
import logging

LOGGER = logging.getLogger(__name__)
```


