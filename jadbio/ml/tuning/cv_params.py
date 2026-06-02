from jadbio.ml.tuning.cv_protocol import CVProtocol, CV


def auto():
    return CVParams(None, None, None, None)


def custom_repeats(repeats: int):
    return CVParams(None, CV(repeats, None), None, None)


def standard_cv(folds, repeats):
    return CVParams(None, CV(repeats, folds), None, None, None)

class CVParams:
    metric_to_optimize = None
    protocol = None
    is_time_series = None
    group_factor = None
    progress_update_config = None
    model_rules_config = None
    disable_dropping = None
    disable_correction = None
    enforce_stopping: bool = None

    def __init__(self, metric, protocol, is_time_series, group_factor, progress_update_config: str = None,
                 model_rules_config: str = None, disable_dropping = None, disable_correction = None,
                 enforce_stopping: bool = None):
        self.metric_to_optimize = metric
        self.protocol = protocol
        self.is_time_series = is_time_series
        self.group_factor = group_factor
        self.progress_update_config = progress_update_config
        self.model_rules_config = model_rules_config
        self.disable_dropping = disable_dropping
        self.disable_correction = disable_correction
        self.enforce_stopping = enforce_stopping

    def with_disabled_progress_update(self):
        return CVParams(
            metric=self.metric_to_optimize,
            protocol=self.protocol,
            is_time_series=self.is_time_series,
            group_factor=self.group_factor,
            progress_update_config='COUNTER',
            model_rules_config=self.model_rules_config,
            disable_dropping=self.disable_dropping,
            disable_correction=self.disable_correction,
            enforce_stopping=self.enforce_stopping
        )

    def with_no_model_rules(self):
        return CVParams(
            metric=self.metric_to_optimize,
            protocol=self.protocol,
            is_time_series=self.is_time_series,
            group_factor=self.group_factor,
            progress_update_config=self.progress_update_config,
            model_rules_config='NONE',
            disable_dropping=self.disable_dropping,
            disable_correction=self.disable_correction,
            enforce_stopping=self.enforce_stopping
        )

    def with_best_model_rule(self):
        return CVParams(
            metric=self.metric_to_optimize,
            protocol=self.protocol,
            is_time_series=self.is_time_series,
            group_factor=self.group_factor,
            progress_update_config=self.progress_update_config,
            model_rules_config='BEST',
            disable_dropping=self.disable_dropping,
            disable_correction=self.disable_correction,
            enforce_stopping=self.enforce_stopping
        )

    def with_custom_protocol(self, protocol: CVProtocol):
        return CVParams(
            metric=self.metric_to_optimize,
            protocol=protocol,
            is_time_series=self.is_time_series,
            group_factor=self.group_factor,
            progress_update_config=self.progress_update_config,
            model_rules_config=self.model_rules_config,
            disable_dropping=self.disable_dropping,
            disable_correction=self.disable_correction,
            enforce_stopping=self.enforce_stopping
        )

    def with_disabled_dropping(self):
        return CVParams(
            metric=self.metric_to_optimize,
            protocol=self.protocol,
            is_time_series=self.is_time_series,
            group_factor=self.group_factor,
            progress_update_config=self.progress_update_config,
            model_rules_config=self.model_rules_config,
            disable_dropping=True,
            disable_correction=self.disable_correction,
            enforce_stopping=self.enforce_stopping
        )

    def with_disabled_correction(self):
        return CVParams(
            metric=self.metric_to_optimize,
            protocol=self.protocol,
            is_time_series=self.is_time_series,
            group_factor=self.group_factor,
            progress_update_config=self.progress_update_config,
            model_rules_config=self.model_rules_config,
            disable_dropping=self.disable_dropping,
            disable_correction=True,
            enforce_stopping=self.enforce_stopping
        )

    def with_optimized_metric(self, metric: str):
        return CVParams(
            metric=metric,
            protocol=self.protocol,
            is_time_series=self.is_time_series,
            group_factor=self.group_factor,
            progress_update_config=self.progress_update_config,
            model_rules_config=self.model_rules_config,
            disable_dropping=self.disable_dropping,
            disable_correction=self.disable_correction,
            enforce_stopping=self.enforce_stopping
        )

    def with_enforced_stopping(self):
        return CVParams(
            metric=self.metric_to_optimize,
            protocol=self.protocol,
            is_time_series=self.is_time_series,
            group_factor=self.group_factor,
            progress_update_config=self.progress_update_config,
            model_rules_config=self.model_rules_config,
            disable_dropping=self.disable_dropping,
            disable_correction=self.disable_correction,
            enforce_stopping=True
        )

    def to_dict(self):
        return {
            'metric2Optimize': self.metric_to_optimize,
            'protocol': self.protocol.to_dict() if self.protocol is not None else None,
            'isTimeSeries': self.is_time_series,
            'groupFactor': self.group_factor,
            'progressUpdateConfig': self.progress_update_config,
            'modelRulesConfig': self.model_rules_config,
            'disableDropping': self.disable_dropping,
            'disableCorrection': self.disable_correction,
            'enableStopping': self.enforce_stopping
        }
