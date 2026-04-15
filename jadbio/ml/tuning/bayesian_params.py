def multiple_acquisitions():
    return {
        'type': 'multiple-acq'
    }


def batch(batch_size: int = None):
    return {
        'type': 'batch',
        'batchSize': batch_size
    }
