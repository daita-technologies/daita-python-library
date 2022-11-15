import os
import requests
import time
from tqdm import tqdm
from daita.footer import footer

endpointCreatePresignUrlSinglefile = os.environ["CREATE_PRESIGN_SIGNLE_URL"]
endpointUploadCompressfile = os.environ["UPLOAD_COMPRESS_FILE"]
endpointTaskProgress = os.environ["TASK_PROGRESS"]


def get_task(id_token, task_id):
    responseTaskProgress = requests.get(
        endpointTaskProgress, params={"id_token": id_token, "task_id": task_id}
    )
    return responseTaskProgress


def upload_compress_file(filename, daita_token):
    resp = requests.post(
        endpointCreatePresignUrlSinglefile,
        json={"filename": os.path.basename(filename), "daita_token": daita_token},
    )
    preSignUrlResult = resp.json()["data"]
    s3_uri = preSignUrlResult["s3_uri"]
    files = {"file": open(filename, "rb")}
    requests.post(
        preSignUrlResult["presign_url"]["url"],
        data=preSignUrlResult["presign_url"]["fields"],
        files=files,
    )

    responseTask = get_task(id_token, task_id)
    data = responseTask.json()
    data = data["data"]["data"]
    task_id = data["task_id"]
    id_token = data["id_token"]

    print(data["message"])
    print(f"Check task id {task_id} on https://dev.daita.tech/my-tasks")
    responseTaskProgress = get_task(id_token, task_id)
    jsonTaskProgress = responseTaskProgress.json()

    if jsonTaskProgress["body"]["message"] != "OK":
        footer()
    data = jsonTaskProgress["body"]["data"]

    number_finished = data["number_finished"]
    with tqdm(total=number_finished, file=sys.stdout) as pbar:
        while True:
            task = get_task(id_token, task_id)
            jsonData = task.json()["body"]["data"]
            if jsonData["status"] == "ERROR":
                print(
                    "Currently your task is error, please check on https://dev.daita.tech/my-tasks"
                )
                footer()
                break
            number_gen_images = int(jsonData["number_gen_images"])
            pbar.update(number_gen_images)
            if number_gen_images == number_finished:
                break
            time.sleep(2)
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
