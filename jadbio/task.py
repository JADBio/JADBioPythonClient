import json
import time

import requests

from jadbio_internal.api.auth import json_headers
from jadbio_internal.api.job import Job


def __get_task_state(host:str, token: str, task_id: str):
    return requests.post(
        host + '/api/data_array/get_task_state',
        headers = json_headers(token),
        data=json.dumps({'id': task_id}),
        verify=True
    )

def wait_for_job(host: str, token: str, job: Job):
    while True:
        resp = __get_task_state(host, token, job.id)
        if not resp.ok:
            print(resp.content)
            raise
        resp_body = json.loads(resp.content)
        status = resp_body['state']
        if(status=='ERROR'):
            print('ERROR')
            raise
        elif(status=='FINISHED'):
            print('FINISHED 100%')
            return resp_body['did']
        else:
            print('RUNNING')
            time.sleep(1)