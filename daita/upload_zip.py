import os
import requests
import time
from datetime import timedelta
from daita.footer import footer
from timeit import default_timer as timer

endpointCreatePresignUrlSinglefile = os.environ["CREATE_PRESIGNED_SINGLE_URL"]
endpointUploadCompressfile = os.environ["UPLOAD_COMPRESSED_FILE"]
endpointTaskProgress = os.environ["TASK_PROGRESS"]


def get_task(id_token, task_id):
    responseTaskProgress = requests.get(
        endpointTaskProgress, params={"id_token": id_token, "task_id": task_id}
    )
    return responseTaskProgress


def upload_compress_file(filename, daita_token):
    resp = requests.post(
        endpointCreatePresignUrlSinglefile,
        json={
            "filename": os.path.basename(filename),
            "daita_token": daita_token,
            "is_zip": True,
        },
    )

    respJson = resp.json()
    if respJson["error"] != False:
        print("Failed to create a presigned URL: {}".format(respJson["message"]))
        footer()

    preSignUrlResult = respJson["data"]
    s3_uri = preSignUrlResult["s3_uri"]
    files = {"file": open(filename, "rb")}
    requests.post(
        preSignUrlResult["presign_url"]["url"],
        data=preSignUrlResult["presign_url"]["fields"],
        files=files,
    )

    responseTask = requests.post(
        endpointUploadCompressfile, json={"s3": s3_uri, "daita_token": daita_token}
    )
    data = responseTask.json()
    print(data["message"])
    data = data["data"]["data"]
    task_id = data["task_id"]
    id_token = data["id_token"]

    print(f"Check your task ID {task_id} on https://app.daita.tech/my-tasks.")

    start = timer()
    while True:
        task = get_task(id_token, task_id)
        taskJson = task.json()
        jsonData = taskJson["data"]
        message = taskJson["message"]
        if taskJson["error"] != False:
            print(message)
            footer()
        end = timer()
        currentStatus = "Status: {st}, Time: {ti}".format(
            st=jsonData["status"], ti=timedelta(seconds=end - start)
        )
        print(currentStatus.ljust(os.get_terminal_size().columns - 1), end="\r")
        if jsonData["status"] == "ERROR":
            print(
                "Your task is currently broken, please check https://app.daita.tech/my-tasks."
            )
            footer()
        elif jsonData["status"] == "FINISH":
            break
        time.sleep(1)
    footer()


def listCompressFiles(files):
    for index, file in enumerate(files):
        print(f"{index} : {file}")
    while True:
        indexTmp = int(input("File selected:"))
        if indexTmp < len(files):
            break
        else:
            print("Please select again!")
    return files[indexTmp]


def dashboardCompressFiles(files, daita_token):
    fileSelected = None
    if len(files) == 1:
        fileSelected = files[0]
    else:
        fileSelected = listCompressFiles(files)
    upload_compress_file(fileSelected, daita_token)
