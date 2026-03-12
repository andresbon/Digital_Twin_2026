class DigitalTwinBundle:
    def __init__(
        self,
        models_by_target,
        features_by_target,
        thresholds_by_target,
        meta,
        leak_cols_by_target
    ):
        self.models_by_target = models_by_target
        self.features_by_target = features_by_target
        self.thresholds_by_target = thresholds_by_target
        self.meta = meta
        self.leak_cols_by_target = leak_cols_by_target