import json
import ntpath

import requests
from requests import Session
from requests_toolbelt import MultipartEncoder

API_VERSION = 'v1'


class RequestFailed(Exception):
    pass


class JadRequestResponseError(Exception):
    """
    Exception raised when sth goes wrong with a request
    """

    def __init__(self, resp: dict, where):
        """
        Initializes an Exception instance using a response dictionary
        :param resp: the response of a request
        :param where: in which operation the error occured
        """

        message = where + ': '
        if 'message' in resp:
            message += resp['message']
        if 'code' in resp:
            message += ', code: ' + resp['code']
        super().__init__(message)


class JadbioClient(object):
    """
    This class provides major JADBio functionality to python users using API calls.
    Requests are HTTP GET and POST only.
    POST requests are used for any kind of resource creation, mutation, or deletion.
    GET requests are read-only and idempotent.
    """

    __base_url = None
    __session = None
    __token = None

    def __init__(self, username: str, password: str, host: str = None):
        """
        Handles communication with the backend.

        :param str username: Jad account username or email.
        :param str password: Jad account password.
        :param str host: Host endpoint (no need to be set).
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        """

        host = 'https://jadapi.jadbio.com' if host is None else host
        self.__base_url = host + '/api/public/{}/'.format(API_VERSION)
        self.__session = None
        self.login(username, password)

    def __del__(self):
        try:
            self.__session.close()
            self.logout()
        except:
            pass

    def get_version(self):
        """
        Provides access to the full version number of the currently deployed API.
        The major version number is always implied by the request URL.

        :return: public api version
        :rtype: str
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> print(client.get_version())
        1.0-beta
        """

        url = self.__base_url + 'version'
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get Version')['version']

    def login(self, username: str, password: str):
        """
        Login user, and store credentials in current session (previous credentials if any, are overwritten).
        Creates a session in the current client instance.

        :param str username: Jad account username or email.
        :param str password: Jad account password.
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.login('anothermail@gmail.com', 'another password')
        """

        self.__session = Session()

        url = self.__base_url + 'login'
        loginRequest = {'usernameOrEmail': username, 'password': password}
        res = self.__session.post(url, json=loginRequest)

        login = JadbioClient.__parse_response__(res, 'Login')

        self.__token = {'Authorization': ' '.join(['Bearer', login['token']])}

    def logout(self):
        """
        Logout. Removes credentials from session.
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.logout()
        """

        self.__session.close()
        self.__token = None

    def create_project(self, name: str, descr: str = ''):
        """
        Creates a new project.

        :param str name: Project name.
        :param str descr: Project description.
        :return: projectID
        :rtype: str
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.create_project("this_is_a_project_name")
        '314'
        """

        url = self.__base_url + 'createProject'
        projectRequest = {'name': name, 'description': descr}
        res = self.__session.post(url,
                                  json=projectRequest,
                                  headers=self.__token)
        return str(
            JadbioClient.__parse_response__(res,
                                            'Create project')['projectId'])

    def get_project(self, project_id: str):
        """
        Returns a project.

        :param str project_id: identifies the project to which the user must have read access.
        :return: { projectId: string, name: string, description?: string }
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_project("314")
        { projectId: '314', name: 'this_is_a_project_name' }
        """

        url = self.__base_url + 'project/{}'.format(project_id)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get project')

    def get_projects(self, offset: int = 0, count: int = 10):
        """
        Projects form an ordered list from which the request extracts the sublist starting at offset and containing at
        most count elements.

        :param int offset: project list offset.
        :param int count: max number of projects to get.
        :return: {offset: number, totalCount: number, data: [{ projectId: string, name: string, description?: string }]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The list uses zero-based indexing, meaning the first element is at offset 0.
        Constraints: Both offset and count must be non-negative integers and count can be at most 100.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_projects()
        {'offset': 0, 'totalCount': 1,
            'data': [{'projectId': '462', 'name': 'test'}]}
        """

        url = self.__base_url + 'projects/owned/{}/{}'.format(offset, count)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get projects')

    def delete_project(self, project_id: str):
        """
        Allows clients to delete a specified project.
        **Beware** This operation silently deletes all contained datasets, analyses and models used inside that project.

        :param str project_id: Identifies the project. It must be owned by the user.
        :return: { projectId: string, name: string, description?: string }
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.delete_project(client.create_project("this_is_a_project_name"))
        {'projectId': '463', 'name': 'this_is_a_project_name'}
        """

        url = self.__base_url + 'project/{}/delete'.format(project_id)
        ret = self.__session.post(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Delete project')

    def upload_file(self, file_id: int, pth_to_file: str):
        """
        Allows clients to upload files to be analyzed.

        :param int file_id:

            The fileId is an alpha-numeric identifier provided by the client. Reusing the fileId will
            overwrite the uploaded file. The fileId must be specified in subsequent requests to create a dataset from
            the raw uploaded file. The file to upload is provided directly as the body of the request.

        :param str pth_to_file: path/to/file to be uploaded.
        :return: file_id
        :rtype: int
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.upload_file(1234, "pth/to/file.csv")
        1234
        """
        with open(pth_to_file, 'r') as f:
            url = self.__base_url + 'file/{}/upload'.format(file_id)
            ret = self.__session.post(url, data=f.read(), headers=self.__token)

            if ret.status_code != 200:
                JadbioClient.__request_failed__(ret, 'Upload file')
        return file_id

    def create_dataset(self,
                       name: str,
                       project_id: str,
                       file_id: int,
                       file_size_in_bytes: int,
                       separator: str = ',',
                       has_samples_in_rows: bool = True,
                       has_feature_headers_name: bool = True,
                       has_sample_headers: bool = True,
                       description: str = ''):
        """
        Create a dataset from an uploaded file.

        :param str name: Name of the dataset (must have at least 3 and at most 60 characters and must be unique within
            the target project).
        :param str project_id: Id of the project to which the dataset will be created.
        :param int file_id: Id provided by the client when the file was uploaded.
        :param int file_size_in_bytes: must match the actual size of the uploaded file.
            (e.g. len(open("pth/to/file.csv",'r').read()))
        :param str separator: specifies the characters used to separate values in the file.
        :param bool has_samples_in_rows: must be true iff rows of the uploaded file correspond to samples.
        :param bool has_feature_headers_name: True if dataset contains feature names.
        :param bool has_sample_headers: True if dataset contains sample names.
        :param str description: Description of created dataset (can be at most 255 characters).
        :return: taskId
        :rtype: str
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> from os.path import getsize
        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> pid = client.create_project("this_is_a_project_name")
        >>> fid = client.upload_file(1234, "pth/to/file.csv")
        >>> client.create_dataset('file', pid, fid,
        ...    len(open("pth/to/file.csv",'r').read()), has_sample_headers=False)
        '689'
        """

        url = self.__base_url + 'file/{}/createDataset'.format(file_id)
        create_dataset_request = {
            'fileSizeInBytes': file_size_in_bytes,
            'separator': separator,
            'hasSamplesInRows': has_samples_in_rows,
            'hasFeatureHeaders': has_feature_headers_name,
            'hasSampleHeaders': has_sample_headers,
            'name': name,
            'description': description,
            'projectId': str(project_id)
        }
        ret = self.__session.post(url,
                                  json=create_dataset_request,
                                  headers=self.__token)
        return str(
            JadbioClient.__parse_response__(ret, 'Create dataset')['taskId'])

    def get_dataset(self, dataset_id: str):
        """
        Returns details of a specific dataset.

        :param str dataset_id: Identifies the dataset which must belong to a project to which the user must have
            read access.
        :return: {datasetId: string, projectId: string, name: string, description?: string, sampleCount: number,
            featureCount: number, sizeInBytes: number}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_dataset('6065')
        {'projectId': '462', 'datasetId': '6075', 'name': 'datasetName',
                    'sampleCount': 150, 'featureCount': 6, 'sizeInBytes': 4507}
        """

        url = self.__base_url + 'dataset/{}'.format(dataset_id)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get dataset')

    def attach_dataset(self, name: str, project_id: str, dataset_id: str):
        """
        Attach a dataset from another project, to a destination project.

        :param str name: Used to name the new dataset. It must have at least 3 and at most 60 characters and must
            be unique within the target project.
        :param str project_id: The destination project where the specified dataset will be attached to. The user should
            have read and write permissions for that project.
        :param str dataset_id:  Identifies the source dataset. It must belong to a project to which the user has read
            permissions.
        :return: {datasetId: string, projectId: string, name: string, description?: string, sampleCount: number,
            featureCount: number, sizeInBytes: number}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.attach_dataset('name_of_attached_dataset', '462','6065')
        {'projectId': '462', 'datasetId': '6065', 'name': 'a new name',
                    'sampleCount': 150, 'featureCount': 6, 'sizeInBytes': 4507}
        """

        url = self.__base_url + 'dataset/{}/attachToProject/{}'.format(dataset_id, project_id)
        ret = self.__session.post(url, data=name, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Attach dataset')

    def get_datasets(self, project_id: str, offset: int = 0, count: int = 10):
        """
        The projectId identifies the project to which the user must have read permissions.
        Datasets form an ordered list from which the request extracts the sublist starting at offset and containing at
        most count elements.
        The list uses zero-based indexing, meaning the first element is at offset 0.

        :param str project_id: Id of the project to get datasets from.
        :param int offset: Start index.
        :param int count: Number of datasets to retrieve.
        :return: { projectId: string, offset: number, totalCount: number,\
            data: [{projectId: string,
                datasetId: string,
                name: string,
                description?: string,
                sampleCount: number,
                featureCount: number,
                sizeInBytes: number}]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The list uses zero-based indexing, meaning the first element is at offset 0.
        Constraints: Both offset and count must be non-negative integers and count can be at most 100.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_datasets('462')
        {'projectId': '462', 'offset': 0, 'totalCount': 2, 'data': [
                {'projectId': '462', 'datasetId': '6065', 'name': 'file',
                    'sampleCount': 150, 'featureCount': 6, 'sizeInBytes': 4507}
            ]}
        """

        url = self.__base_url + 'datasets/{}/{}/{}'.format(
            project_id, offset, count)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get datasets')

    def delete_dataset(self, dataset_id: str):
        """
        Delete a specified dataset.
        Beware that this operation silently deletes all associated analyses and model uses.

        :param str dataset_id: Identifies the dataset. It must belong to a project to which the user has write
            permissions.
        :return: {datasetId: string, name: string, description?: string, sampleCount: number, featureCount: number,
            sizeInBytes: number}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.delete_dataset('6065')
        {'datasetId': '6065', 'name': 'file', 'sampleCount': 150,
            'featureCount': 6, 'sizeInBytes': 4507}
        """

        url = self.__base_url + 'dataset/{}/delete'.format(dataset_id)
        ret = self.__session.post(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Delete dataset')

    def change_feature_types(self, dataset_id: str, new_name: str,
                             changes: list):
        """
        Create an alternative versions of a specified dataset using different feature types.

        :param str dataset_id:  Identifies the source dataset. It must belong to a project to which the user has read
            and write permissions. The new dataset will be attached to that same project.
        :param str new_name: Used to name the new dataset. It must have at least 3 and at most 60 characters and must
            be unique within the target project.
        :param list changes: list of { matcher: dict, newType: string }. Each element of the changes array matches some
            features of the source dataset as specified by the matcher field. The types of those features in the new
            dataset will be changed to the type given by newType whose value must be one of numerical, categorical,
            timeToEvent, event, or identifier. If some feature is matched by multiple matchers, the last matching entry
            in the changes array determines its new type.

            **'byName'** field provides the exact names of the features to match

            { matcher: { "byName": [name1,...,nameN] }, newType: string }

            **'byIndex'** field provides the 0-based column indices of the features to match

            { matcher: { "byIndex": [id1,...,idN] }, newType: string }

            'byCurrentType' field provides the current type of the features to match.
            It must be one of 'numerical', 'categorical', 'timeToEvent', 'event', or 'identifier'.

            { matcher: { "byCurrentType": string }, newType: string }

            **'byDeducedType'**  field provides the "deduced" type of the features to match.
            It must be either categorical or identifier. Features have "deduced" types in cases where feature data did
            not provide sufficient clarity about the intended type, and so JADBio deduced a type on a best-effort basis.

            { matcher: { "byDeducedType": string }, newType: string }

        :return: taskId
        :rtype: str
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> changes = [{'matcher': {'byName': ['variable1']},
        ...    'newType': 'categorical'}]
        >>> client.change_feature_types('6065', 'file_cat', changes)
        '691'
        >>> import time
        >>> time.sleep(3) # normally this would be done in a while loop
        >>> client.get_task_status('691')
        {'taskId': '691', 'state': 'finished', 'datasetIds': ['6067'],
                'datasetId': '6067'}
        """

        url = self.__base_url + 'dataset/{}/changeFeatureTypes'.format(
            dataset_id)
        change_feature_types_request = {
            'newName': new_name,
            'changes': changes
        }
        ret = self.__session.post(url,
                                  json=change_feature_types_request,
                                  headers=self.__token)
        return str(
            JadbioClient.__parse_response__(ret,
                                            'Change feature types')['taskId'])

    def change_feature_types_check(self, dataset_id: str, new_name: str,
                                   changes: list):
        """
        Check for possible warnings and/or errors in the creation of an alternative version of a specified dataset
        using different feature types.

        :param str dataset_id:  Identifies the source dataset. It must belong to a project to which the user has read
            and write permissions. The new dataset will be attached to that same project.
        :param str new_name: Used to name the new dataset. It must have at least 3 and at most 60 characters and must
            be unique within the target project.
        :param list changes: list of { matcher: dict, newType: string }. Each element of the changes array matches some
            features of the source dataset as specified by the matcher field. The types of those features in the new
            dataset will be changed to the type given by newType whose value must be one of numerical, categorical,
            timeToEvent, event, or identifier. If some feature is matched by multiple matchers, the last matching entry
            in the changes array determines its new type.

            **'byName'** field provides the exact names of the features to match

            { matcher: { "byName": [name1,...,nameN] }, newType: string }

            **'byIndex'** field provides the 0-based column indices of the features to match

            { matcher: { "byIndex": [id1,...,idN] }, newType: string }

            'byCurrentType' field provides the current type of the features to match.
            It must be one of 'numerical', 'categorical', 'timeToEvent', 'event', or 'identifier'.

            { matcher: { "byCurrentType": string }, newType: string }

            **'byDeducedType'**  field provides the "deduced" type of the features to match.
            It must be either categorical or identifier. Features have "deduced" types in cases where feature data did
            not provide sufficient clarity about the intended type, and so JADBio deduced a type on a best-effort basis.

            { matcher: { "byDeducedType": string }, newType: string }

        :return: {errors?: [string], warnings?: [string], suggestions?: [string]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> changes = [{'matcher': {'byName': ['variable1']},
        ...    'newType': 'numerical'}]
        >>> client.change_feature_types_check('6065', 'file_cat', changes)
        {"warnings: ["IdentityTransformation"]}
        """

        url = self.__base_url + 'dataset/{}/check/changeFeatureTypes'.format(
            dataset_id)
        change_feature_types_request = {
            'newName': new_name,
            'changes': changes
        }
        ret = self.__session.post(url,
                                  json=change_feature_types_request,
                                  headers=self.__token)
        return JadbioClient.__parse_response__(ret,
                                               'Check change feature types')

    def get_task_status(self, task_id: str):
        """
        Returns the status of an asynchronous task running on the server.

        :param str task_id: The identity of the task.
        :return: {taskId: string, state: string, datasetId?: string, datasetIds?: [string]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_task_status('689')
        {'taskId': '689', 'state': 'finished', 'datasetIds': ['6065'],
                                                        'datasetId': '6065'}
        """

        url = self.__base_url + 'task/{}/status'.format(task_id)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get task')

    def analyze_dataset(self,
                        dataset_id: str,
                        name: str,
                        outcome: dict,
                        thoroughness: str = 'preliminary',
                        core_count: int = 1,
                        grouping_feat: str = None,
                        models_considered: str = 'all',
                        feature_selection: str = 'mostRelevant',
                        max_signature_size=None,
                        max_visualized_signature_count=None):
        """
        Initiate an analysis of a specified dataset.

        :param str dataset_id: Identity of a dataset attached to a project to which the user has execute permissions.
        :param str name: Provides the analysis with a human-readable name for future reference. The name can be at most
            120 characters long.
        :param dict outcome: dictionary. Specifies both the type of analysis intended, and the dataset feature or
            features that  are to be predicted.

            Regression analysis: outcome = {'regression': 'target_variable_name'}

            Classification analysis: outcome = {'classification': 'target_variable_name'}

            Survival analysis: outcome = {'survival': {
                                                        'event': 'event_variable_name',
                                                        'timeToEvent': 'time_to_event_variable_name'
                                                        }}

        :param str grouping_feat: Specifies an Identifier feature that groups samples which must not be split across
            training and test datasets during analysis, e.g. because they are repeated measurements from the same
            patient (optional).
        :param str models_considered:  must be either 'interpretable' or 'all' This parameter controls the types of
            model considered during the search for the best one. Interpretable models include only models that are easy
            to interpret such as linear models and decision trees.
        :param str feature_selection: must be either 'mostRelevant' or 'mostRelevantOrAll' (optional).
        :param str thoroughness:  must be one of 'preliminary', 'typical', or extensive. This parameter is used to
            reduce or expand the number of analysis configurations attempted in the search for the best ones;
            it significantly affects the running time of the analysis.
        :param int core_count: Positive integer. It specifies the number of compute cores to use during the analysis,
            and must be at most the number of cores currently available to the user.
        :param int max_signature_size: The maximum number of features used in a model found by the analysis.
            When present, it must be a positive integer. When not present, a default value of 25 is used.
        :param int max_visualized_signature_count: The maximum number of signatures that will be prepared for
            visualization in the user interface. When present, it must be a positive integer.
            When not present, a default value of 5 is used.
        :return: analysis_id
        :rtype: str
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.analyze_dataset('6067', 'file_classification',
        ...    {'classification': 'variable1'})
        '5219'
        """

        url = self.__base_url + 'dataset/{}/analyze'.format(dataset_id)
        ret = self.__analyze_dataset__(name, outcome, thoroughness, core_count,
                                       grouping_feat, models_considered,
                                       feature_selection, max_signature_size,
                                       max_visualized_signature_count, None, None,
                                       url)
        return str(
            JadbioClient.__parse_response__(ret,
                                            'Analyze dataset')['analysisId'])

    def analyze_dataset_check(self,
                              dataset_id: str,
                              name: str,
                              outcome: dict,
                              thoroughness: str = 'preliminary',
                              core_count: int = 1,
                              grouping_feat: str = None,
                              models_considered: str = 'all',
                              feature_selection: str = 'mostRelevant',
                              max_signature_size=None,
                              max_visualized_signature_count=None):
        """
        Check for possible errors and warnings, if an analysis is run on a specified dataset.

        :param str dataset_id: Identity of a dataset attached to a project to which the user has execute permissions.
        :param str name: Provides the analysis with a human-readable name for future reference. The name can be at most
            120 characters long.
        :param dict outcome: dictionary. Specifies both the type of analysis intended, and the dataset feature or
            features that  are to be predicted.

            Regression analysis: outcome = {'regression': 'target_variable_name'}

            Classification analysis: outcome = {'classification': 'target_variable_name'}

            Survival analysis: outcome = {'survival': {
                                                        'event': 'event_variable_name',
                                                        'timeToEvent': 'time_to_event_variable_name'
                                                        }}

        :param str grouping_feat: Specifies an Identifier feature that groups samples which must not be split across
            training and test datasets during analysis, e.g. because they are repeated measurements from the same
            patient (optional).
        :param str models_considered:  must be either 'interpretable' or 'all' This parameter controls the types of
            model considered during the search for the best one. Interpretable models include only models that are easy
            to interpret such as linear models and decision trees.
        :param str feature_selection: must be either 'mostRelevant' or 'mostRelevantOrAll' (optional).
        :param str thoroughness:  must be one of 'preliminary', 'typical', or extensive. This parameter is used to
            reduce or expand the number of analysis configurations attempted in the search for the best ones;
            it significantly affects the running time of the analysis.
        :param int core_count: Positive integer. It specifies the number of compute cores to use during the analysis,
            and must be at most the number of cores currently available to the user.
        :param int max_signature_size: The maximum number of features used in a model found by the analysis.
            When present, it must be a positive integer. When not present, a default value of 25 is used.
        :param int max_visualized_signature_count: The maximum number of signatures that will be prepared for
            visualization in the user interface. When present, it must be a positive integer.
            When not present, a default value of 5 is used.
        :return: {errors?: [string], warnings?: [string], suggestions?: [string]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.analyze_dataset_check('2310', 'file_classification',
        ...    {'classification': 'target'})
        {
            "errors": ["SubscriptionDoesNotSupportExtensiveAnalysis",
                "CoreCountLimitExceeded"],
            "warnings: ["TooFewSamplesPerClassForAnalysis"]
        }
        """

        url = self.__base_url + 'dataset/{}/check/analyze'.format(dataset_id)
        ret = self.__analyze_dataset__(name, outcome, thoroughness, core_count,
                                       grouping_feat, models_considered,
                                       feature_selection, max_signature_size,
                                       max_visualized_signature_count, None, None,
                                       url)

        return JadbioClient.__parse_response__(ret, 'Analyze dataset check')

    def analyze_dataset_extra_models(self,
                                     dataset_id: str,
                                     name: str,
                                     outcome: dict,
                                     extra_models: list = None,
                                     extra_feature_selectors: list = None,
                                     thoroughness: str = 'preliminary',
                                     core_count: int = 1,
                                     grouping_feat: str = None,
                                     models_considered: str = 'all',
                                     feature_selection: str = 'mostRelevant',
                                     max_signature_size=None,
                                     max_visualized_signature_count=None):
        """
        Initiate an analysis of a specified dataset, with additional models specified by the user.
        These models are added to be trained in the analysis on top of the models that JADBio selects using its AI system.

        :param str dataset_id: Identity of a dataset attached to a project to which the user has execute permissions.
        :param str name: Provides the analysis with a human-readable name for future reference. The name can be at most
            120 characters long.
        :param dict outcome: dictionary. Specifies both the type of analysis intended, and the dataset feature or
            features that  are to be predicted.

            Regression analysis: outcome = {'regression': 'target_variable_name'}

            Classification analysis: outcome = {'classification': 'target_variable_name'}

            Survival analysis: outcome = {'survival': {
                                                        'event': 'event_variable_name',
                                                        'timeToEvent': 'time_to_event_variable_name'
                                                        }}
        :param list extra_models: specifies extra models along with their hyperparameters, to be run in the current
            analysis. Input in the form:
            
            .. code-block:: python
            
                {
                    'name': 'an algorithm name',
                    'parameters': {
                        'paramName1': paramValue1, 
                        'paramName2': paramValue2,
                        ...
                    }
                }[]
        :param list extra_feature_selectors: specifies extra featureSelectors along with their hyperparameters,
            to be run in the current analysis. Input in the form:

            .. code-block:: python

                {
                    'name': 'an algorithm name',
                    'parameters': {
                        'paramName1': paramValue1,
                        'paramName2': paramValue2,
                        ...
                    }
                }[]
        :param str grouping_feat: Specifies an Identifier feature that groups samples which must not be split across
            training and test datasets during analysis, e.g. because they are repeated measurements from the same
            patient (optional).
        :param str models_considered:  must be either 'interpretable' or 'all' This parameter controls the types of
            model considered during the search for the best one. Interpretable models include only models that are easy
            to interpret such as linear models and decision trees.
        :param str feature_selection: must be either 'mostRelevant' or 'mostRelevantOrAll' (optional).
        :param str thoroughness:  must be one of 'preliminary', 'typical', or extensive. This parameter is used to
            reduce or expand the number of analysis configurations attempted in the search for the best ones;
            it significantly affects the running time of the analysis.
        :param int core_count: Positive integer. It specifies the number of compute cores to use during the analysis,
            and must be at most the number of cores currently available to the user.
        :param int max_signature_size: The maximum number of features used in a model found by the analysis.
            When present, it must be a positive integer. When not present, a default value of 25 is used.
        :param int max_visualized_signature_count: The maximum number of signatures that will be prepared for
            visualization in the user interface. When present, it must be a positive integer.
            When not present, a default value of 5 is used.
        :return: analysis_id
        :rtype: str
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> knn = [{'name': 'KNeighborsClassifier', 'parameters': {'n_neighbors': 5}}]
        >>> client.analyze_dataset_extra_models('6067', 'file_classification',
        ...    {'classification': 'variable1'}, extra_models=knn)
        '5219'
        """

        url = self.__base_url + 'dataset/{}/extra/analyze'.format(
            dataset_id)
        ret = self.__analyze_dataset__(name, outcome, thoroughness, core_count,
                                       grouping_feat, models_considered,
                                       feature_selection, max_signature_size,
                                       max_visualized_signature_count,
                                       extra_models, extra_feature_selectors, url)
        return str(
            JadbioClient.__parse_response__(ret,
                                            'Analyze dataset')['analysisId'])

    def analyze_dataset_extra_models_check(
            self,
            dataset_id: str,
            name: str,
            outcome: dict,
            extra_models: list = None,
            extra_feature_selectors: list = None,
            thoroughness: str = 'preliminary',
            core_count: int = 1,
            grouping_feat: str = None,
            models_considered: str = 'all',
            feature_selection: str = 'mostRelevant',
            max_signature_size=None,
            max_visualized_signature_count=None):
        """
        Check for possible errors and warnings, if an analysis with extra algorithms is run on a specified dataset.

        :param str dataset_id: Identity of a dataset attached to a project to which the user has execute permissions.
        :param str name: Provides the analysis with a human-readable name for future reference. The name can be at most
            120 characters long.
        :param dict outcome: dictionary. Specifies both the type of analysis intended, and the dataset feature or
            features that  are to be predicted.

            Regression analysis: outcome = {'regression': 'target_variable_name'}

            Classification analysis: outcome = {'classification': 'target_variable_name'}

            Survival analysis: outcome = {'survival': {
                                                        'event': 'event_variable_name',
                                                        'timeToEvent': 'time_to_event_variable_name'
                                                        }}
        :param list extra_models: specifies extra models along with their hyperparameters, to be run in the current
            analysis. Input in the form:
            
            .. code-block:: python
            
                {
                    'name': 'an algorithm name',
                    'parameters': {
                        'paramName1': paramValue1, 
                        'paramName2': paramValue2,
                        ...
                    }
                }[]
        :param list extra_feature_selectors: specifies extra featureSelectors along with their hyperparameters,
            to be run in the current analysis. Input in the form:

            .. code-block:: python

                {
                    'name': 'an algorithm name',
                    'parameters': {
                        'paramName1': paramValue1,
                        'paramName2': paramValue2,
                        ...
                    }
                }[]
        :param str grouping_feat: Specifies an Identifier feature that groups samples which must not be split across
            training and test datasets during analysis, e.g. because they are repeated measurements from the same
            patient (optional).
        :param str models_considered:  must be either 'interpretable' or 'all' This parameter controls the types of
            model considered during the search for the best one. Interpretable models include only models that are easy
            to interpret such as linear models and decision trees.
        :param str feature_selection: must be either 'mostRelevant' or 'mostRelevantOrAll' (optional).
        :param str thoroughness:  must be one of 'preliminary', 'typical', or extensive. This parameter is used to
            reduce or expand the number of analysis configurations attempted in the search for the best ones;
            it significantly affects the running time of the analysis.
        :param int core_count: Positive integer. It specifies the number of compute cores to use during the analysis,
            and must be at most the number of cores currently available to the user.
        :param int max_signature_size: The maximum number of features used in a model found by the analysis.
            When present, it must be a positive integer. When not present, a default value of 25 is used.
        :param int max_visualized_signature_count: The maximum number of signatures that will be prepared for
            visualization in the user interface. When present, it must be a positive integer.
            When not present, a default value of 5 is used.
        :return: {errors?: [string], warnings?: [string], suggestions?: [string]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> knn = [{'name': 'KNeighborsClassifier', 'parameters': {'n_neighbors': 5}}]
        >>> client.analyze_dataset_extra_models_check('2310', 'file_classification',
        ...    {'classification': 'target'})
        {
            "errors": ["SubscriptionDoesNotSupportExtensiveAnalysis",
                "CoreCountLimitExceeded"],
            "warnings: ["TooFewSamplesPerClassForAnalysis"]
        }
        """

        url = self.__base_url + 'dataset/{}/extra/check/analyze'.format(
            dataset_id)
        ret = self.__analyze_dataset__(name, outcome, thoroughness, core_count,
                                       grouping_feat, models_considered,
                                       feature_selection, max_signature_size,
                                       max_visualized_signature_count,
                                       extra_models, extra_feature_selectors, url)

        return JadbioClient.__parse_response__(ret, 'Analyze dataset check')

    def get_extra_models_description(self, outcome_type: str):
        """
        Retrieves descriptions for extra available models that can be explicitly added to an analysis.
        These models can be added to be trained in the analysis on top of the models that JADBio selects using its AI system.

        :param str outcome_type: must be either 'regression, 'classification', or 'survival'. This parameter specifies
            the type of extra models to be retrieved.
        :return: {name: string, description: string, type: string, parameters: object[]}[]
        :rtype: list
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_extra_models_description('classification')
        [
            {'name': alg1Name,'description': alg1description,'type':alg1type,
                'parameters':[{'name': param1,'description':param1descr,
                        'type': ['int'], 'defaultValue': 5,
                        'possibleValues':[{'min':minVal,'max':maxVal},...]},
                        ...
                        ]
            },
            ...
        ]
        """

        url = self.__base_url + 'analysis/extra/{}/models'.format(outcome_type)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(
            ret, 'Get Extra Models')['extraModels']

    def get_extra_fs_description(self, outcome_type: str):
        """
        Retrieves descriptions for extra available feature selectors that can be explicitly added to an analysis.
        These feature selectors can be added to be trained in the analysis on top of the algorithms that JADBio selects using its AI system.

        :param str outcome_type: must be either 'regression, 'classification', or 'survival'. This parameter specifies
            the type of extra models to be retrieved.
        :return: {name: string, description: string, type: string, parameters: object[]}[]
        :rtype: list
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_extra_models_description('classification')
        [
            {'name': alg1Name,'description': alg1description,'type':alg1type,
                'parameters':[{'name': param1,'description':param1descr,
                        'type': ['int'], 'defaultValue': 5,
                        'possibleValues':[{'min':minVal,'max':maxVal},...]},
                        ...
                        ]
            },
            ...
        ]
        """

        url = self.__base_url + 'analysis/extra/{}/featureSelectors'.format(outcome_type)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(
            ret, 'Get Extra FS')['extraFeatureSelectors']

    def get_analysis(self, analysis_id: str):
        """
        Returns an analysis.

        :param str analysis_id: Identifies the analysis which must belong to a project to which the user must
            have read access.
        :return: {analysisId: string, projectId: string, parameters: object, state: string}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_analysis('5219')
        {
            'analysisId': '5219',
            'projectId': '462',
            'parameters': {
                'coreCount': 1
                'datasetId': '6067',
                'featureSelection': 'mostRelevant',
                'maxSignatureSize': 25,
                'maxVisualizedSignatureCount': 5,
                'modelsConsidered': 'all',
                'name': 'file_classification',
                'outcome': {'classification': 'variable1'},
                'thoroughness': 'preliminary'},
            'state': 'finished'}
        }
        """

        url = self.__base_url + 'analysis/{}'.format(analysis_id)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get analysis')

    def get_analyses(self, project_id: str, offset: int = 0, count: int = 10):
        """
        Returns a sublist of all analyses in a project.

        :param str project_id: Identifies the project to which the user must have read permission.
        :param int offset: Request extracts the sublist starting at offset.
        :param int count: max number of analyses to get.
        :return: {projectId: string, offset: number, totalCount: number, \
            data: [{analysisId: string, parameters: object, state: string}]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The list uses zero-based indexing, meaning the first element is at offset 0.
        Constraints: Both offset and count must be non-negative integers and count can be at most 100.
        The parameters object has the same fields as specified when each analysis was created,
        including the dataset identifier and optional values.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_analyses('462')
        {'projectId': '462', 'offset': 0, 'totalCount': 1, 'data': [{
            'analysisId': '5219',
            'projectId': '462',
            'parameters': {
                'coreCount': 1
                'datasetId': '6067',
                'featureSelection': 'mostRelevant',
                'maxSignatureSize': 25,
                'maxVisualizedSignatureCount': 5,
                'modelsConsidered': 'all',
                'name': 'file_classification',
                'outcome': {'classification': 'variable1'},
                'thoroughness': 'preliminary'},
                'state': 'finished'}]}
        """

        url = self.__base_url + 'analyses/all/{}/{}/{}'.format(
            project_id, offset, count)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get analyses')

    def get_analysis_status(self, analysis_id: str):
        """
        Returns the status of an analysis.

        :param str analysis_id: Identifies the analysis. It must belong to a project to which the user has read
            permissions.
        :return: {analysisId: string, parameters: object, state: string, startTime?: timestamp, \
            executionTimeInSeconds?: number, progress?: number}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The nested parameters object has the same fields as specified when the analysis was created,
        including the dataset identifier and optional values.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_analysis_status('5219')
        {
            'analysisId': '5219',
            'projectId': '462',
            'parameters': {
                'coreCount': 1
                'datasetId': '6067',
                'featureSelection': 'mostRelevant',
                'maxSignatureSize': 25,
                'maxVisualizedSignatureCount': 5,
                'modelsConsidered': 'all',
                'name': 'file_classification',
                'outcome': {'classification': 'variable1'},
                'thoroughness': 'preliminary'},
            'state': 'finished',
            'startTime': '2021-02-26T11:04:15Z',
            'executionTimeInSeconds': 10}
        """

        url = self.__base_url + 'analysis/{}/status'.format(analysis_id)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get analysis status')

    def get_analysis_result(self, analysis_id: str):
        """
        Returns the result of a finished analysis.

        :param str analysis_id: Identifies the analysis.
        :return: {analysisId: string, parameters: object, mlEngine: string, startTime: timestamp,\
            executionTimeInSeconds: number, models: { model_key1?: model1, model_key2?: model2}}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The nested parameters object has the same fields as specified when the analysis was created,
        including the identity of the dataset and optional values.

        The model datatype has the following form: {preprocessing: string, featureSelection: string, model: string,
            signatures: string[][], performance: {key: value,}}.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_analysis_result('5219')
        {'mlEngine': 'jadbio-1.1.0', 'analysisId': '5219',
            'parameters': {
                'coreCount': 1
                'datasetId': '6067',
                'featureSelection': 'mostRelevant',
                'maxSignatureSize': 25,
                'maxVisualizedSignatureCount': 5,
                'modelsConsidered': 'all',
                'name': 'file_classification',
                'outcome': {'classification': 'variable1'},
                'thoroughness': 'preliminary'},
            'models': {
                'best': {
                    'preprocessing': 'Constant Removal, Standardization',
                    'featureSelection': 'Test-Budgeted Statistically Equivalent
                        Signature (SES) algorithm with hyper-parameters:
                        maxK = 2, alpha = 0.05 and budget = 3 * nvars',
                    'model': 'Support Vector Machines (SVM) of type C-SVC with
                        Polynomial Kernel and hyper-parameters:  cost = 1.0,
                        gamma = 1.0, degree = 3',
                    'signatures': [["variable5", "variable4"]],
                    "performance": {
                          "Area Under the ROC Curve": 0.9979193891504624,
                      }},
                'interpretable': {
                    'preprocessing': 'Constant Removal, Standardization',
                    'featureSelection': 'Test-Budgeted Statistically Equivalent
                        Signature (SES) algorithm with hyper-parameters:
                        maxK = 2, alpha = 0.05 and budget = 3 * nvars',
                    'model': 'Classification Decision Tree with Deviance
                        splitting criterion and hyper-parameters: minimum
                        leaf size = 3, and pruning parameter alpha = 0.05',
                    'signatures': [["variable5", "variable4"]],
                    "performance": {
                      "Area Under the ROC Curve": 0.951428730938,
                    }},
            },
            'startTime': '2021-02-26T11:04:15Z', 'executionTimeInSeconds': 10}
        """

        url = self.__base_url + 'analysis/{}/result'.format(analysis_id)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get analysis result')

    def delete_analysis(self, analysis_id: str):
        """
        Allows clients to delete a specified analysis.

        :param str analysis_id: Identifies the analysis. It must belong to a project to which the user has
            write permissions.
        :return: {analysisId: string, parameters: object, state: string}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The parameters object has the same fields as specified when each analysis was created,
        including the dataset identifier and optional values.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.delete_analysis('5219')
        {'analysisId': '5219', 'projectId': '462',
            'parameters': {
                'coreCount': 1
                'datasetId': '6067',
                'featureSelection': 'mostRelevant',
                'maxSignatureSize': 25,
                'maxVisualizedSignatureCount': 5,
                'modelsConsidered': 'all',
                'name': 'file_classification',
                'outcome': {'classification': 'variable1'},
                'thoroughness': 'preliminary'},
            'state': 'finished'}
        """

        url = self.__base_url + 'analysis/{}/delete'.format(analysis_id)
        ret = self.__session.post(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Delete analysis')

    def available_plots(self, analysis_id: str, model_key: str):
        """
        Retrieves the plot names of the computed plots for a given model in an analysis.

        :param str analysis_id: Identifies the analysis.
        :param str model_key: A key present in analysis_result['models'] (e.g. 'best' or 'interpretable')
        :return: {analysisId: string, modelKey: string, plots: string[]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The analysisId, modelKey is the same as in the request. The plots array contains the plot names that are
        available for the current modelKey.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.available_plots('5219', "best")
        {'analysisId': '5219', 'modelKey': 'best',
            'plots': ['Feature Importance', 'Progressive Feature Importance']}
        """

        url = self.__base_url + 'analysis/{}/availablePlots?modelKey={}'.format(
            analysis_id, model_key)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Available analysis')

    def get_plot(self, analysis_id: str, model_key: str, plot_key: str):
        """
        Retrieves the raw values of a plot for a modelKey - analysis pair.

        :param str analysis_id: Identifies the analysis.
        :param str model_key: A key present in analysis_result['models'] (e.g. 'best' or 'interpretable')
        :param str plot_key: A key present in available_plots['plots'] (e.g. 'Feature Importance')
        :return: {analysis_id: string, modelKey: string, plot: {plot_key: object}}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The analysisId, model_key are the same as in the request. The plot object contains the raw values of the
        requested plot.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_plot('5219', "best", "Progressive Feature Importance")
        {'analysisId': '5219', 'modelKey': 'best',
            'plot': {
                'Progressive Feature Importance': [
                    {
                        'name': ['variable5'],
                        'cis': [0.9826582435278086, 1.0],
                        'value': 0.9946595460614152},
                    {
                        'name': ['variable5', 'variable4'],
                        'cis': [1.0, 1.0],
                        'value': 1.0}]}
        }

        """

        url = self.__base_url + 'analysis/{}/getPlot?modelKey={}&plotKey={}'.format(
            analysis_id, model_key, plot_key)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get plot')

    def get_plots(self, analysis_id: str, model_key: str):
        """
        Retrieves the raw values of all the available plots for a modelKey - analysis pair.

        :param str analysis_id: Identifies the analysis.
        :param str model_key: A key present in analysis_result['models'] (e.g. 'best' or 'interpretable')
        :return: {analysis_id: string, model_key: string, plots: {plot_key: object}[]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The analysisId, model_key are the same as in the request. The plots array contains the raw values of plot
        objects per plotKey present in the request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_plots('5219', "best")
        {'analysisId': '5548', 'modelKey': 'best',
            'plots': [
                {'Feature Importance': [{
                    'name': 'variable5',
                    'cis': [0.0, 0.017277777777777836],
                    'value': '0.0053404539385848585'},
                    {'name': 'variable4',
                    'cis': [0.0, 0.017341756472191352],
                    'value': '0.0053404539385848585'}]},
                {'Progressive Feature Importance': [{
                    'name': ['variable5'],
                    'cis': [0.9826582435278086, 1.0],
                    'value': 0.9946595460614152},
                    {'name': ['variable5', 'variable4'],
                    'cis': [1.0, 1.0],
                    'value': 1.0}]}]}

        """

        url = self.__base_url + 'analysis/{}/getPlots?modelKey={}'.format(
            analysis_id, model_key)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get plots')

    def predict_outcome(self,
                        analysis_id: str,
                        dataset_id: str,
                        model_key: str,
                        signature_index: int = 0):
        """
        Launches a task that predicts outcome for an unlabeled dataset using a model found by a finished analysis.
        (User must have read and execute permissions to the project that contains the analysis and the dataset to be
        predicted.)

        :param str analysis_id: Identifies the analysis, must belong to the same project as the dataset_id.
        :param str dataset_id: Identifies a dataset containing unlabeled data, must belong to the same project as
            analysis_id.
        :param str model_key: A key present in analysis_result['models'] (e.g. 'best' or 'interpretable')
        :param int signature_index: zero-based index of the model signature to use for the predictions.
        :return: predictionId
        :rtype: str
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.predict_outcome('5219', '6067', 'best')
        '431'
        """

        url = self.__base_url + 'analysis/{}/predict/{}'.format(
            analysis_id, dataset_id)
        predict_outcome_request = {
            'modelKey': model_key,
            'signatureIndex': signature_index
        }
        ret = self.__session.post(url,
                                  json=predict_outcome_request,
                                  headers=self.__token)
        return str(
            JadbioClient.__parse_response__(ret,
                                            'Predict outcome')['predictionId'])

    def predict_outcome_check(self,
                              analysis_id: str,
                              dataset_id: str,
                              model_key: str,
                              signature_index: int = 0):
        """
        Launches a task that predicts outcome for an unlabeled dataset using a model found by a finished analysis.
        (User must have read and execute permissions to the project that contains the analysis and the dataset to be
        predicted.)

        :param str analysis_id: Identifies the analysis, must belong to the same project as the dataset_id.
        :param str dataset_id: Identifies a dataset containing unlabeled data, must belong to the same project as
            analysis_id.
        :param str model_key: A key present in analysis_result['models'] (e.g. 'best' or 'interpretable')
        :param int signature_index: zero-based index of the model signature to use for the predictions.
        :return: {errors?: [string], warnings?: [string], suggestions?: [string]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:TestDataContainsSignatureFeatureCategoryNotInTrainingData

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.predict_outcome_check('5219', '6067', 'best')
        {
            "errors": ["TestDataContainsSignatureFeatureCategoryNotInTrainingData"]
        }
        """

        url = self.__base_url + 'analysis/{}/check/predict/{}'.format(
            analysis_id, dataset_id)
        predict_outcome_request = {
            'modelKey': model_key,
            'signatureIndex': signature_index
        }
        ret = self.__session.post(url,
                                  json=predict_outcome_request,
                                  headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Check Predict outcome')

    def get_prediction(self, prediction_id: str):
        """
        Returns a prediction.

        :param str prediction_id: Identifies the prediction which must belong to a project to which the user
            has read access.
        :return: {predictionId: string, projectId: string, parameters: object, state: string}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_prediction('431')
        {
            'projectId': '462',
            'predictionId': '431',
            'parameters': {'analysisId': '5219',
                'modelKey': 'best',
                'signatureIndex': 0,
                'datasetId': '6067'
                },
            'state': 'finished'
        }
        """

        url = self.__base_url + 'prediction/{}'.format(prediction_id)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get prediction')

    def get_predictions(self,
                        analysis_id: str,
                        offset: int = 0,
                        count: int = 10):
        """
        Returns a sublist of the predictions created using an analysis result.

        :param str analysis_id: Identifies the analysis which must belong to a project to which the user has
            read permissions.
        :param int offset: predictions list offset.
        :param count: max number of predictions to get.
        :return: {analysisId: string, offset: number, totalCount: number,
            data: [{predictionId: string, projectId: string, parameters: object, state: string}]}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        The list uses zero-based indexing, meaning the first element is at offset 0.
        Constraints: Both offset and count must be non-negative integers and count can be at most 100.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_predictions('5219')
        {
            'analysisId': '5219'
            'offset': 0,
            'totalCount': 1,
            'data': [{
                'projectId': '462',
                'predictionId': '431',
                'parameters': {'analysisId': '5219',
                    'modelKey': 'best',
                    'signatureIndex': 0,
                    'datasetId': '6067'
                    },
                'state': 'finished'
            }],
        }
        """

        url = self.__base_url + 'analysis/{}/predictions/{}/{}'.format(
            analysis_id, offset, count)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get predictions')

    def get_prediction_status(self, prediction_id: str):
        """
        Returns the status of a prediction.

        :param str prediction_id: Identifies a prediction in a project to which the user has read permissions.
        :return: {predictionId: string, state: string, progress?: number}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_prediction_status('431')
        {'predictionId': '431', 'state': 'finished'}
        """

        url = self.__base_url + 'prediction/{}/status'.format(prediction_id)
        ret = self.__session.get(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Get prediction status')

    def get_prediction_result(self, prediction_id: str):
        """
        Downloads the result of a finished prediction task.

        :param str prediction_id: Identifies a prediction in a project to which the user has read permissions.
        :return: predictions in csv format
        :rtype: str
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.get_prediction_result('431')
        "Sample name,Prob ( class = firstcat ),Prob ( class = scndcat ),
                                                    Prob ( class = thirdCat )
        1,0.9890362674058242,0.0046441918237983175,0.006319540770377525
        2,0.9890362674058242,0.0046441918237983175,0.006319540770377525
        3,0.9930412181618086,0.0031263130498427327,0.003832468788348629
        ...
        ...
        ..."
        """

        url = self.__base_url + 'prediction/{}/result?format=csv'.format(
            prediction_id)
        ret = self.__session.get(url, headers=self.__token)
        if ret.status_code != 200:
            JadbioClient.__request_failed__(ret, "Get prediction result")
        return ret.content.decode("utf-8")

    def delete_prediction(self, prediction_id: str):
        """
        Allows clients to delete a specified prediction.

        :param str prediction_id: Identifies the prediction. It must belong to a project to which
            the user has write permissions.
        :return: {predictionId: string, projectId: string, parameters: object, state: string}
        :rtype: dict
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client = JadbioClient('juser@gmail.com', 'a password')
        >>> client.delete_prediction('431')
        {'projectId': '462', 'predictionId': '431',
            'parameters': {'analysisId': '5219',
                'modelKey': 'best',
                'signatureIndex': 0,
                'datasetId': '6067'
                },
            'state': 'finished'
        }
        """

        url = self.__base_url + 'prediction/{}/delete'.format(prediction_id)
        ret = self.__session.post(url, headers=self.__token)
        return JadbioClient.__parse_response__(ret, 'Delete prediction')

    def image_upload_init(self,
                          project_id: str,
                          name: str,
                          data_path: str,
                          has_feature_names: bool = True,
                          description: str = None):
        """
        :param str project_id: project id
        :param str name: image name (should be unique per project)
        :param str data_path: csv file containing sample names, target, other features, if None it defaults to 'target.csv'
        :param bool has_feature_names:
        :param str description: dataset description (optional)
        :return: {taskId: string}
        :raises RequestFailed, JadRequestResponseError: Exception in case sth goes wrong with a request.

        :Example:

        >>> client.image_upload_init(10, 'image_dataset', '/path/to/data')
        """

        url = self.__base_url + 'image/initUpload'
        data_file = "target.csv" if data_path is None else data_path

        encoded_data = MultipartEncoder(
            fields={
                'attributes':
                json.dumps({
                    'projectId': project_id,
                    'name': name,
                    'description': description,
                    'hasFeatureHeaders': has_feature_names
                }),
                'file': ('target.csv', open(data_file, 'rb'), 'text/plain'),
            })
        ret = requests.post(url,
                            data=encoded_data,
                            headers={
                                'Content-Type': encoded_data.content_type,
                                'Authorization': self.__token['Authorization']
                            },
                            verify=True)
        return JadbioClient.__parse_response__(ret,
                                               'Image Upload init')['taskId']

    def image_upload_add_sample(self, task_id: str, sample: str, path: str):
        url = self.__base_url + 'image/{}/add'.format(task_id)

        # Platform-independent method to get path (see https://stackoverflow.com/a/8384788)
        head, tail = ntpath.split(path)
        fname = tail or ntpath.basename(head)
        encoded_data = MultipartEncoder(
            fields={
                'sampleId': sample,
                'file': (fname, open(path, 'rb'), 'text/plain')
            })
        ret = requests.post(url,
                            data=encoded_data,
                            headers={
                                'Content-Type': encoded_data.content_type,
                                'Authorization': self.__token['Authorization']
                            })
        return JadbioClient.__parse_response__(ret, 'Image Sample Upload')

    def image_upload_commit(self, task_id: str):
        url = self.__base_url + 'image/{}/commit'.format(task_id)
        ret = requests.get(url, headers=__json_headers__(self.__token))
        return JadbioClient.__parse_response__(ret, 'Image Upload Commit')

    # ---------------Private-Functions------------------------------------------#
    def __analyze_dataset__(self, name, outcome, thoroughness, core_count,
                            grouping_feat, models_considered,
                            feature_selection, max_signature_size,
                            max_visualized_signature_count, extra_models, extra_fs, url):

        analyze_dataset_request = {
            'outcome': outcome,
            'modelsConsidered': models_considered,
            'featureSelection': feature_selection,
            'thoroughness': thoroughness,
            'coreCount': core_count,
            'name': name
        }
        if max_visualized_signature_count is not None:
            analyze_dataset_request[
                'maxVisualizedSignatureCount'] = max_visualized_signature_count
        if max_signature_size is not None:
            analyze_dataset_request['maxSignatureSize'] = max_signature_size
        if grouping_feat is not None:
            analyze_dataset_request['groupingFeature'] = grouping_feat
        if extra_models is not None:
            analyze_dataset_request['extraModels'] = JadbioClient.__extra_algs_to_json__(extra_models)
        if extra_fs is not None:
            analyze_dataset_request['extraFeatureSelectors'] = JadbioClient.__extra_algs_to_json__(extra_fs)

        return self.__session.post(url,
                                   json=analyze_dataset_request,
                                   headers=self.__token)

    @staticmethod
    def __extra_algs_to_json__(extra_models):
        extra_models_json = list()
        for model in extra_models:
            parameters = list()
            for k2, v2 in model['parameters'].items():
                parameters.append({'key': k2, 'value': v2})
            extra_models_json.append({
                'name': model['name'],
                'parameters': parameters
            })
        return extra_models_json

    @staticmethod
    def __parse_response__(resp, where):
        if resp.status_code != 200:
            JadbioClient.__request_failed__(resp, where)
        res = resp.json()
        if res['status'] != 'success':
            raise JadRequestResponseError(res, where)
        return res['payload']

    @staticmethod
    def __request_failed__(res, where: str):
        """
        Throws exception if request has failed
        :param res:
        :param str where: during which public function call did the request fail
        :return:
        """
        ret = where + ": " + str(res)
        if hasattr(res, 'content'):
            ret += ', message: ' + str(res.content.decode("utf-8"))
        raise RequestFailed(ret)


def __json_headers__(token):
    return {
        'Content-type': 'application/json',
        'Authorization': token['Authorization']
    }
