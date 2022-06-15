import os
import csv
import requests
import supervisely as sly
from supervisely.app.v1.app_service import AppService
import json
import pathlib
import random
import google.api_core.exceptions as google_exceptions
from google.cloud import storage

my_app: AppService = AppService(ignore_task_id=True)
links = None # list of dicts
previewLinks = None # list of lists (raw csv)
gs_key_local_path = os.path.join(my_app.data_dir, "key.json")
gcs_client = None

ACTION_IGNORE = "ignore"
ACTION_ADD_TO_META = "add to image as meta information"
#ACTION_ADD_TO_TAGS = "add to image as tags"

TEAM_ID = int(os.environ['context.teamId'])


def _download_csv_file(api, remote_path):
    local_path = os.path.join(my_app.data_dir, "file.csv")
    sly.fs.ensure_base_path(local_path)
    api.file.download(TEAM_ID, remote_path, local_path)
    return local_path


@my_app.callback("stop")
@sly.timeit
def stop(api: sly.Api, task_id, context, state, app_logger):
    remote_path = "/temp/{}/".format(task_id)
    api.file.remove(TEAM_ID, remote_path)


@my_app.callback("preview_csv")
@sly.timeit
def preview_csv(api: sly.Api, task_id, context, state, app_logger):
    global links, previewLinks
    remote_path = state["csvPath"]
    downloaded = False
    error_text = ""
    try:
        local_path = _download_csv_file(api, remote_path)
        downloaded = True
    except requests.exceptions.HTTPError as e:
        error_text = json.loads(e.response.text)

    table = {"columns": [], "data": []}
    if downloaded is True:
        with open(local_path) as f:
            links = list(csv.DictReader(f))
        with open(local_path) as f:
            previewLinks = list(csv.reader(f))
        table = {"columns": previewLinks[0], "data": previewLinks[1:5+1]}

    fields = [{"field": "data.previewTable", "payload": table},
              {"field": "data.csvDownloadError", "payload": error_text},]

    if downloaded is True:
        fields.append({"field": "state.urlColumn", "payload": previewLinks[0][0]}),
    api.app.set_fields(task_id, fields)
    if downloaded is True:
        sly.fs.silent_remove(local_path)

def _transform(uri, state):
    if state["transformUri"] is True:
        res = uri.replace(state["suffixBefore"], state["suffixAfter"])
        return res
    else:
        return uri

@my_app.callback("transform_uri")
@sly.timeit
def transform_uri(api: sly.Api, task_id, context, state, app_logger):
    columns = previewLinks[0]
    uri_index = columns.index(state["urlColumn"])
    results = []
    for row in previewLinks[1:5 + 1]:
        new_row = row.copy()
        new_row[uri_index] = _transform(new_row[uri_index], state)
        results.append(new_row)

    table = {"columns": columns, "data": results}
    fields = [{"field": "data.transformedTable", "payload": table}]
    api.app.set_fields(task_id, fields)


def download_gcp_image(gcs_client, remote_path, local_path):
    p = pathlib.Path(remote_path)
    bucket_name = p.parts[2]
    source_blob_name = os.path.join(*p.parts[3:])

    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(local_path)


@my_app.callback("validate_creds")
@sly.timeit
def validate_creds(api: sly.Api, task_id, context, state, app_logger):
    global gcs_client
    api.task.set_field(task_id, "data.credError", "")

    api.file.download(TEAM_ID, state["credsPath"], gs_key_local_path)
    rand_url = random.choice(links)[state["urlColumn"]]
    rand_url = _transform(rand_url, state)
    file_name = sly.fs.get_file_name_with_ext(rand_url)
    gcs_client = storage.Client.from_service_account_json(gs_key_local_path)
    preview_image_local_path = os.path.join(my_app.data_dir, file_name)
    try:
        download_gcp_image(gcs_client, rand_url, preview_image_local_path)
    #except google_exceptions.GoogleAPICallError as e:
    except Exception as e:
        api.task.set_field(task_id, "data.credError", rand_url + " : " + str(e))
        return
    remote_path = "/temp/{}/{}".format(task_id, file_name)
    api.file.remove(TEAM_ID, remote_path)
    file_info = api.file.upload(TEAM_ID, preview_image_local_path, remote_path)
    sly.fs.silent_remove(preview_image_local_path)

    api.task.set_field(task_id, "data.previewImageUrl", file_info.storage_path)
    pass

@my_app.callback("upload")
@sly.timeit
def upload(api: sly.Api, task_id, context, state, app_logger):
    fields = [{"field": "data.uploadError", "payload": ""},
              {"field": "data.uploadStarted", "payload": True}]
    api.app.set_fields(task_id, fields)

    workspace_name = state["workspaceName"]
    if not workspace_name:
        api.task.set_field(task_id, "data.uploadError", "Workspace name is not defined")
        return

    project_name = state["projectName"]
    if not project_name:
        api.task.set_field(task_id, "data.uploadError", "Project name is not defined")
        return

    dataset_name = state["datasetName"]
    if not dataset_name:
        api.task.set_field(task_id, "data.uploadError", "Dataset name is not defined")
        return

    workspace = api.workspace.get_info_by_name(TEAM_ID, workspace_name)
    if workspace is None:
        workspace = api.workspace.create(TEAM_ID, workspace_name)

    project = api.project.get_info_by_name(workspace.id, project_name)
    if project is None:
        project = api.project.create(workspace.id, project_name)

    dataset = api.dataset.get_info_by_name(project.id, dataset_name)
    if dataset is None:
        dataset = api.dataset.create(project.id, dataset_name)

    if gcs_client is None:
        api.task.set_field(task_id, "data.uploadError", "Error: Validate creds step is skipped")
        return

    existing_names = api.image.get_list(dataset.id)
    existing_names = set([info.name for info in existing_names])
    _total_count = len(links)
    _uploaded_count = 0
    for batch in sly.batched(links, batch_size=15):
        batch_local_paths = []
        batch_names = []
        batch_metas = []
        for link in batch:
            uri = link[state["urlColumn"]]
            res_url = _transform(uri, state)
            file_name = sly.fs.get_file_name_with_ext(res_url)
            ext = sly.fs.get_file_ext(file_name)
            if not ext:
                file_name += sly.image.DEFAULT_IMG_EXT

            #image_info = api.image.get_info_by_name(dataset.id, file_name)
            need_upload = True
            upload_name = file_name
            if file_name in existing_names:
                if state["skipImage"] is True:
                    need_upload = False
                    continue
                else:
                    #upload_name = api.image.get_free_name(dataset.id, file_name)
                    upload_name = sly._utils.generate_free_name(existing_names, file_name, with_ext=True)


            local_path = os.path.join(my_app.data_dir, file_name)
            try:
                download_gcp_image(gcs_client, res_url, local_path)
                batch_local_paths.append(local_path)
                batch_names.append(upload_name)
                existing_names.add(upload_name)

                if state["otherColumnsAction"] == ACTION_ADD_TO_META:
                    link_meta = link.copy()
                    link_meta.pop(state["urlColumn"], None)
                    batch_metas.append(link_meta)
                else:
                    batch_metas.append({})
            # except google_exceptions.GoogleAPICallError as e:
            except Exception as e:
                app_logger.warn("Link {!r} skipped: {}".format(uri, str(e)))
                continue

            if state["normalizeExif"] is True or state["removeAlphaChannel"] is True:
                img = sly.image.read(local_path, remove_alpha_channel=state["removeAlphaChannel"])
                sly.image.write(local_path, img, remove_alpha_channel=state["removeAlphaChannel"])


        api.image.upload_paths(dataset.id, batch_names, batch_local_paths, metas=batch_metas)
        for local_path in batch_local_paths:
            sly.fs.silent_remove(local_path)

        _uploaded_count += len(batch)

        fields = [{"field": "data.uploadedCount", "payload": _uploaded_count},
                  {"field": "data.totalCount", "payload": _total_count},
                  {"field": "data.uploadProgress", "payload": int(_uploaded_count * 100 / _total_count)}]
        api.app.set_fields(task_id, fields)

    my_app.stop()



def main():
    data = {
        "previewTable": {"columns": [], "data": []},
        "csvDownloadError": "",
        "credError": "",
        "otherColumnsActions": [ACTION_IGNORE, ACTION_ADD_TO_META],#, ACTION_ADD_TO_TAGS],
        "previewImageUrl": "",
        "finished": False,
        "transformedTable": {"columns": [], "data": []},
        "uploadError": "",
        "uploadedCount": 0,
        "totalCount": 0,
        "uploadProgress": 0,
        "uploadStarted": False
    }

    state = {
        "csvPath": "",
        "credsPath": "",
        "urlColumn": "",
        "otherColumnsAction": ACTION_ADD_TO_META,
        "transformUri": True,
        "suffixBefore": "gs://",
        "suffixAfter": "https://storage.cloud.google.com/",
        "workspaceName": "",
        "projectName": "",
        "datasetName": "",
        "normalizeExif": True,
        "removeAlphaChannel": True,
        "skipImage": True
    }

    # @TODO: add upload by link option
    # Run application service
    my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)