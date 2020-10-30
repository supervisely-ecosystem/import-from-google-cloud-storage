import os
import csv
import requests
import supervisely_lib as sly
import json

my_app = sly.AppService()

TEAM_ID = int(os.environ['context.teamId'])

def _download_csv_file(api, remote_path):
    local_path = os.path.join(my_app.data_dir, "/files/file.csv")
    sly.fs.ensure_base_path(local_path)
    api.file.download(TEAM_ID, remote_path, local_path)
    return local_path

@my_app.callback("preview_csv")
@sly.timeit
def preview_csv(api: sly.Api, task_id, context, state, app_logger):
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
            links = list(csv.reader(f))
        table = {
            "columns": links[0],
            "data": links[1:5+1]
        }

    fields = [{"field": "data.previewTable", "payload": table},
              {"field": "data.csvDownloadError", "payload": error_text},]
    api.app.set_fields(task_id, fields)
    if downloaded is True:
        sly.fs.silent_remove(local_path)


@my_app.callback("preprocessing")
@sly.timeit
def preprocessing(api: sly.Api, task_id, context, state, app_logger):
    sly.logger.info("do something here")


def main():
    data = {
        "previewTable": {"columns": [], "data": []},
        "csvDownloadError": ""
    }

    state = {
        "csvPath": "/my_folder/links1.csv"
    }

    initial_events = [
        {"state": None, "context": None, "command": "preprocessing"}
    ]

    #@TODO: csvPath -  set back to empty ""
    # Run application service
    my_app.run(data=data, state=state, initial_events=initial_events)


if __name__ == "__main__":
    sly.main_wrapper("main", main)