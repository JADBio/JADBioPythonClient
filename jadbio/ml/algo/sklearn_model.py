class RandomForestRegressor:
    n_estimators = 100
    criterion = 'squared_error'

    def __init__(
            self,
            n_estimators = 100,
            criterion = 'squared_error',
    ) -> None:
        self.n_estimators = n_estimators
        self.criterion = criterion

    def to_dict(self):
        return {
            'type': 'SKLearnModelTrainer',
            'algName': 'RandomForestRegressor',
            'params': {
                'n_estimators': self.n_estimators,
                'criterion': self.criterion,
            }
        }
