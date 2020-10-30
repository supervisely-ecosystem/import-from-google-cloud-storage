import os
import csv
import requests
import supervisely_lib as sly
import json
import pathlib
from google.cloud import storage

my_app = sly.AppService()
links_dict = None
gs_key_local_path = os.path.join(my_app.data_dir, "key.json")

ACTION_IGNORE = "ignore"
ACTION_ADD_TO_META = "add to image as meta information"
ACTION_ADD_TO_TAGS = "add to image as tags"

TEAM_ID = int(os.environ['context.teamId'])

def _download_csv_file(api, remote_path):
    local_path = os.path.join(my_app.data_dir, "/files/file.csv")
    sly.fs.ensure_base_path(local_path)
    api.file.download(TEAM_ID, remote_path, local_path)
    return local_path

@my_app.callback("preview_csv")
@sly.timeit
def preview_csv(api: sly.Api, task_id, context, state, app_logger):
    global links_dict
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
            links_dict = list(csv.DictReader(f))
        with open(local_path) as f:
            links = list(csv.reader(f))
        table = {"columns": links[0], "data": links[1:5+1]}

    fields = [{"field": "data.previewTable", "payload": table},
              {"field": "data.csvDownloadError", "payload": error_text},]

    if downloaded is True:
        fields.append({"field": "state.urlColumn", "payload": links[0][0]}),
    api.app.set_fields(task_id, fields)
    if downloaded is True:
        sly.fs.silent_remove(local_path)


def download_gcp_image(gcs_client, remote_path, local_path):
    p = pathlib.Path(remote_path)
    bucket_name = p.parts[2]
    source_blob_name = os.path.join(*p.parts[3:])

    bucket = gcs_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(local_path)

@my_app.callback("stop")
@sly.timeit
def stop(api: sly.Api, task_id, context, state, app_logger):
    remote_path = "/temp/{}/".format(task_id)
    api.file.remove(TEAM_ID, remote_path)
    api.task.set_field(task_id, "data.finished", True)

@my_app.callback("validate_creds")
@sly.timeit
def validate_creds(api: sly.Api, task_id, context, state, app_logger):
    api.file.download(TEAM_ID, state["credsPath"], gs_key_local_path)
    first_url = links_dict[0][state["urlColumn"]]
    first_url = first_url.replace("gs://", "https://storage.cloud.google.com/")
    file_name = sly.fs.get_file_name_with_ext(first_url)
    gcs_client = storage.Client.from_service_account_json(gs_key_local_path)
    preview_image_local_path = os.path.join(my_app.data_dir, file_name)
    download_gcp_image(gcs_client, first_url, preview_image_local_path)

    remote_path = "/temp/{}/{}".format(task_id, file_name)
    file_info = api.file.upload(TEAM_ID, preview_image_local_path, remote_path)

    sly.fs.silent_remove(preview_image_local_path)
    pass

def main():
    data = {
        "previewTable": {"columns": [], "data": []},
        "csvDownloadError": "",
        "credError": "",
        "otherColumnsActions": [ACTION_IGNORE, ACTION_ADD_TO_META, ACTION_ADD_TO_TAGS],
        "previewImageUrl": "",
        "finished": False
    }

    state = {
        "csvPath": "/my_folder/links.csv",
        "credsPath": "/my_folder/abc-b017125670ed.json",
        "urlColumn": "",
        "otherColumnsAction": ACTION_IGNORE
    }

    #@TODO: csvPath, credsPath -  set back to empty ""
    # Run application service
    my_app.run(data=data, state=state)


if __name__ == "__main__":
    sly.main_wrapper("main", main)