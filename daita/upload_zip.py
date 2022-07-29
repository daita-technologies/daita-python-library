import os
import requests
from daita.footer import footer

endpointCreatePresignUrlSinglefile = os.environ['CREATE_PRESIGN_SIGNLE_URL']
endpointUploadCompressfile = os.environ['UPLOAD_COMPRESS_FILE']


def upload_compress_file(filename, daita_token):
    resp = requests.post(
        endpointCreatePresignUrlSinglefile,
        json={"filename": os.path.basename(
            filename), "daita_token": daita_token},
    )
    preSignUrlResult = resp.json()["data"]
    s3_uri = preSignUrlResult["s3_uri"]
    files = {"file": open(filename, "rb")}
    requests.post(
        preSignUrlResult["presign_url"]["url"],
        data=preSignUrlResult["presign_url"]["fields"],
        files=files,
    )
    responseTask = requests.post(
        endpointUploadCompressfile, json={
            "s3": s3_uri, "daita_token": daita_token}
    )
    data = responseTask.json()
    task_id = data["data"]["data"]["task_id"]
    print(data["message"])
    print(f"Check task id {task_id} on https://dev.daita.tech/my-tasks")


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
