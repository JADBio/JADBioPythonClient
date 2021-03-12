from os.path import getsize

import time

# helper function for example
def upload_dataset(client, pth, name, pid, has_snames=True):
    """
    # Uploads (as is) and creates dataset synchronously from file path
    :param client: A client instance
    :param pth: pth/to/file to upload
    :param name: Name of the dataset to be created
    :param pid: Project id
    :param has_snames: Does the dataset have row headers?
    :return: created dataset id
    """

    # Uploads (as is) and creates dataset synchronously from file path
    file_id = 2310
    file_id = client.upload_file(file_id, pth)
    tid = client.create_dataset(name, pid, file_id, getsize(pth), has_sample_headers=has_snames)
    print("Uploaded dataset with tid: " + str(tid))
    status = client.get_task_status(tid)
    while status['state'] != 'finished':
        time.sleep(3)
        status = client.get_task_status(tid)
    return status['datasetId']