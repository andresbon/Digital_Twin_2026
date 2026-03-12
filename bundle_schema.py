from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DigitalTwinBundle:
    
    models_by_target: Dict[str, Any]
    features_by_target: Dict[str, list]
    thresholds_by_target: Dict[str, dict]
    leak_cols_by_target: Dict[str, list]
    meta: Dict[str, Any]