#!/usr/bin/env python
# Assumes the images are stored in a flat directory
# that has a 'target.csv' file containing
# the sample between file names and the target

import time

import jadbio.client as jad
import os

SUPPORTED_IMAGE_TYPES = ['jpeg', 'jpg', 'tif', 'png', 'bmp']


def image_files_in_dir(dir: str):
    return [
        f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f))
        and f.split(".")[1] in SUPPORTED_IMAGE_TYPES
    ]


def wait_for_job(client: jadbio.client.JadbioClient, task: str):
    while True:
        resp_body = client.get_task_status(task)
        status = resp_body['state'].upper()
        if (status == 'ERROR'):
            print('ERROR')
            raise
        elif (status == 'FINISHED'):
            print('FINISHED 100%')
            return resp_body['datasetId']
        else:
            print('RUNNING')
            time.sleep(1)


project = 1607
# path to a directory that contains the images, along with a
# target.csv file of the following format
# headers, target, ...
# sample1, 1
# sample2, 0
# sample3, 1
# ...

location = '/path/to/client/histo/'
client = jad.JadbioClient('user', 'pass')

image_files = image_files_in_dir(location)
task = client.image_upload_init(project, 'image', location + '/target.csv',
                                True)
for image_file in image_files:
    sample = image_file.split('.')[0]
    client.image_upload_add_sample(task, sample, location + '/' + image_file)
client.image_upload_commit(task)
dataset_id = wait_for_job(client, task)
