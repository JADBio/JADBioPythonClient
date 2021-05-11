#!/usr/bin/env python
import tempfile
import time

import jadbio.client as jad
import os
SUPPORTED_IMAGE_TYPES = ['jpeg', 'jpg', 'tif', 'png', 'bmp']

def write_target_dict_to_tmp(dict: dict):
    fd, path = tempfile.mkstemp()
    with os.fdopen(fd, 'w') as tmp:
        tmp.write('header,target\n')
        for (sample_key, target) in dict.items():
            tmp.write(f'{sample_key},{target}\n')
    return path

def image_files_in_dir(dir: str):
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.split(".")[1] in SUPPORTED_IMAGE_TYPES]


def wait_for_job(client: jadbio.client.JadbioClient, task: str):
    while True:
        resp_body = client.get_task_status(task)
        status = resp_body['state'].upper()
        if(status=='ERROR'):
            print('ERROR')
            raise
        elif(status=='FINISHED'):
            print('FINISHED 100%')
            return resp_body['datasetId']
        else:
            print('RUNNING')
            time.sleep(1)

def upload_type2(
        jadbio_client: jadbio.client.JadbioClient,
        project: int,
        name: str,
        data_folder: str,
        description: str = None
):
    class_names = os.listdir(data_folder)
    if (len(class_names) < 2):
        raise (f'Classes found {len(class_names)}')

    class_dict = {}
    sample_path_dict = {}
    for target_class in class_names:
        image_files = image_files_in_dir(os.path.join(data_folder, target_class))

        for image_file in image_files:
            sample = image_file.split('.')[0]
            class_dict[sample] = target_class
            sample_path_dict[sample] = os.path.join(data_folder, target_class, image_file)

    try:
        target_path = write_target_dict_to_tmp(class_dict)
        with open(target_path, "r") as myfile:
            print(myfile.readlines())
        task = jadbio_client.image_upload_init(project, name, target_path, True, description)
        for sample, sample_path in sample_path_dict.items():
            print('Adding sample {}'.format(sample))
            jadbio_client.image_upload_add_sample(task, sample, sample_path)
        jadbio_client.image_upload_commit(task)
        return wait_for_job(jadbio_client, task)
    finally:
        os.remove(target_path)

client = jad.JadbioClient('user', 'pass')

project = 11
# This kind of upload works only for classification
# It is assumed that the directory has the following format
#folder
#   -> class1
#       -> img1
#       -> img2
#       ...
#   -> class2
#       -> img3
#       -> img4
#       ...
#   ...
location = '/path/to/image'
d = upload_type2(jadbio_client=client, project=project, name='image', data_folder=location)
