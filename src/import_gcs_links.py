import os
import csv
import requests
import supervisely_lib as sly
import json

my_app = sly.AppService()
links_dict = None

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

# @my_app.callback("preview_csv")
# @sly.timeit
# def preview_csv(api: sly.Api, task_id, context, state, app_logger):
#     pass

def main():
    data = {
        "previewTable": {"columns": [], "data": []},
        "csvDownloadError": "",
        "credError": "",
        "otherColumnsActions": [ACTION_IGNORE, ACTION_ADD_TO_META, ACTION_ADD_TO_TAGS]
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