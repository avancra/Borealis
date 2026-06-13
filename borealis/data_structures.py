from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DeviceInfo:
    alias: str
    metadata: Dict[str, Any]
