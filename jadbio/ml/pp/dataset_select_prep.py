from typing import List

class DatasetSelectPrep:
    dataset_ids = [0]

    def __init__(self, dataset_ids: List[int]):
        self.dataset_ids = dataset_ids

    def to_dict(self):
        return {
            'type': 'DatasetSelectPreprocessorFactory',
            'datasetIds': self.dataset_ids,
        }