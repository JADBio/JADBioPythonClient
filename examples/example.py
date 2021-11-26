# Press the green button in the gutter to run the script.
import time

import sys
import pathlib
import jadbio.client as jad

if __name__ == '__main__':
    cur_folder_pth = str(pathlib.Path(__file__).parent.absolute())

    # insert to pth so that imports will work
    sys.path.insert(1, cur_folder_pth+"/..")
    from helper import upload_dataset

    pth_to_resources = cur_folder_pth+'/resources'

    # initialize session
    client = jad.JadbioClient('an active JADBio username or email', 'password')
    print("Version: " + client.get_version())
    # create a new project
    pid = client.create_project("this_is_a_name")

    # print projects current user has access to
    print("Projects: " + str(client.get_projects()))
    try:
        print("Created project: "+str(pid))

        # upload and create dataset
        dataset_id = upload_dataset(client, pth_to_resources+"/iris.csv", 'iris', pid)

        # changes to set variable1 of the uploaded dataset as categorical
        changes = [{'matcher': {'byName': ['variable1']}, 'newType': 'categorical'}]

        # check if everything seems ok with current proposed transformation
        possible_warning_error = client.change_feature_types_check(dataset_id, 'iris_cat', changes)
        for key, messages in possible_warning_error.items():
            print(key+": "+str(messages))

            # if errors exist in analysis check, throw an exception
            if 'errors' in key:
                raise Exception("Invalid transformation: "+str(messages))

        # make changes and store modified dataset with name iris_cat
        tid = client.change_feature_types(dataset_id, 'iris_cat', changes)
        status = client.get_task_status(tid)

        # poll every 3 seconds until task is finished
        while status['state'] != 'finished':
            time.sleep(3)
            status = client.get_task_status(tid)

        # get dataset_id when finished
        dataset_id = status['datasetId']

        # define additional models to be run in the current analysis
        extra_models = [{'name': 'KNeighborsClassifier', 'parameters': {'n_neighbors': 5}}]

        # check if everything seems ok with running an analysis with these parameters
        possible_warning_error = client.analyze_dataset_extra_models_check(dataset_id, 'iris_analysis', {'classification': 'variable1'},
                                                              max_signature_size=10, max_visualized_signature_count=50,
                                                              extra_models=extra_models)
        for key, messages in possible_warning_error.items():
            print(key+": "+str(messages))

            # if errors exist in analysis check, throw an exception
            if 'errors' in key:
                raise Exception("Invalid analysis parameters: "+str(messages))

        analysis_id = client.analyze_dataset_extra_models(dataset_id, 'iris_analysis', {'classification': 'variable1'},
                                             max_signature_size=10, max_visualized_signature_count=50,
                                             extra_models=extra_models)

        status = client.get_analysis_status(analysis_id)

        # poll every 3 seconds until task is finished
        while status['state'] != 'finished':
            time.sleep(3)
            status = client.get_analysis_status(analysis_id)
        print("Analysis finished")

        # print analyses performed under project
        print("Analyses: " + str(client.get_analyses(pid)))

        # get result of last analysis
        result = client.get_analysis_result(analysis_id)
        print("Analysis result: " + str(result))

        # upload subset of iris so that it can be used for making predictions
        dataset_id2 = upload_dataset(client, pth_to_resources+"/iris_no_trgt.csv",
                                     'iris_test', pid, False)
        for best_model_key, best_conf in result['models'].items():
            # print the type of each best model found and it's configuration
            print(best_model_key+":\n\t"+str(best_conf))

            # check if everything seems ok with predicting with these parameters an analysis with these parameters
            possible_warning_error = client.predict_outcome_check(analysis_id, dataset_id2, best_model_key)
            for key, messages in possible_warning_error.items():
                print(key + ": " + str(messages))

                # if errors exist in analysis check, throw an exception
                if 'errors' in key:
                    continue

            # create a prediction task on dataset_id2, using the current model
            prediction_id = client.predict_outcome(analysis_id, dataset_id2, best_model_key)

            status = client.get_prediction_status(prediction_id)
            # poll every 3 seconds until task is finished
            while status['state'] != 'finished':
                time.sleep(3)
                status = client.get_prediction_status(prediction_id)

            # print result of prediction, result comes in a csv format
            print("prediction result head:\n\t"+str(client.get_prediction_result(prediction_id).split('\n')[0:5]))

        # delete current analysis
        print("Deleted analysis: " + str(client.delete_analysis(analysis_id)))
        # delete current dataset
        print("Deleted dataset: " + str(client.delete_dataset(dataset_id2)))
    finally:
        # cleanup (a.k.a. delete everything that was created in this example.
        print("Remaining datasets in {}: ".format(pid) + str(client.get_datasets(pid)))

        # Careful! When a project is deleted, all analysis and datasets inside that project will also get deleted
        print("Deleted project" + str(client.delete_project(pid)))

