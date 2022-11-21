import os
import time
import requests
import hashlib
import sys
import queue
import threading
from tqdm import tqdm
from daita.footer import footer
from daita.utils import retry_handler
from itertools import chain, islice

batch_size = 10
endpointPresignURL = os.environ["CREATE_PRESIGNED_SINGLE_URL"]
endpointCheckExistenceFile = os.environ["CHECK_FILE_EXISTENCE"]
endpointUploadUpdate = os.environ["UPLOAD_UPDATE"]

daita_token = None


def batcher(iterable, size):
    iterator = iter(iterable)
    for first in iterator:
        yield list(chain([first], islice(iterator, size - 1)))


@retry_handler(max_retry=10, sleep_time=1)
def put_image_S3(filename):
    resp = requests.post(
        endpointPresignURL,
        json={
            "filename": os.path.basename(filename),
            "daita_token": daita_token,
            "is_zip": False,
        },
    )
    preSignUrlResult = resp.json()["data"]
    files = {"file": open(filename, "rb")}
    requests.post(
        preSignUrlResult["presign_url"]["url"],
        data=preSignUrlResult["presign_url"]["fields"],
        files=files,
    )
    time.sleep(0.5)
    return


def UploadUpdate(filesnames):
    filenamesList = []
    ls_object_info = []
    for it in filesnames:
        with open(it, "rb") as f:
            hash = hashlib.md5(f.read()).hexdigest()
        temp = {
            "s3_key": "",
            "filename": os.path.basename(it),
            "hash": hash,
            "size": os.path.getsize(it),
            "is_ori": True,
            "gen_id": "",
        }
        filenamesList.append(os.path.basename(it))
        ls_object_info.append(temp)

    payload = {
        "filenames": filenamesList,
        "ls_object_info": ls_object_info,
        "daita_token": daita_token,
    }
    preSignUrlResp = requests.post(endpointUploadUpdate, json=payload)
    if preSignUrlResp.status_code != 200:
        print("Something went wrong sorry, please check again")
        print(preSignUrlResp.text)
        footer()
    return


def generator(filenames):
    yield from filenames


class ThreadWorker(threading.Thread):
    def __init__(self, queue, updateQueue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.updateQueue = updateQueue

    def run(self):
        while True:
            filenames = self.queue.get()
            try:
                for it in filenames:
                    put_image_S3(filename=it)
            except Exception as e:
                print("Debug: {}".format(e))
                return

            UploadUpdate(filesnames=filenames)

            self.updateQueue.put(len(filenames))
            self.queue.task_done()


def checkExistenceFile(filenames, daita_token):

    fullfile = {os.path.basename(it): it for it in filenames}
    basenamefilenames = [os.path.basename(it) for it in filenames]

    payload = {"ls_filename": basenamefilenames, "daita_token": daita_token}

    RespcheckExistenceFile = requests.post(endpointCheckExistenceFile, json=payload)

    ResultcheckExistenceFile = RespcheckExistenceFile.json()
    if ResultcheckExistenceFile["error"] == True:
        print(f"Something went wrong with {ResultcheckExistenceFile['message']}")
        os._exit(1)

    if len(ResultcheckExistenceFile["data"]) == 0:
        return filenames
    newFileNotExist = []

    for it in ResultcheckExistenceFile["data"]:
        if it["filename"] in fullfile:
            del fullfile[it["filename"]]

    for v in fullfile.items():
        newFileNotExist.append(v)
    return newFileNotExist


def check_size_image(filenames):
    oldlen = len(filenames)
    newArr = list(
        filter(lambda x: int(os.path.getsize(x) / (1024**2)) <= 5, filenames)
    )
    if oldlen != len(newArr):
        print("Some files are larger than 5MB!")
    return newArr


def upload_images(filenames, token):
    global daita_token
    daita_token = token
    batches = [it for it in batcher(generator(filenames), batch_size)]
    workerQueue = queue.Queue()
    updateProcessbarQueue = queue.Queue()
    for batch in batches:
        workerQueue.put(batch)

    for _ in range(10):
        t = ThreadWorker(queue=workerQueue, updateQueue=updateProcessbarQueue)
        t.setDaemon(True)
        t.start()

    combined = queue.Queue(maxsize=0)

    def listen(q):
        while True:
            combined.put((q, q.get()))

    t1 = threading.Thread(target=listen, args=(updateProcessbarQueue,))
    t1.daemon = True
    t1.start()
    numberFileTotal = len(filenames)
    print(f"Total File: {numberFileTotal}")
    print("STARTING UPLOAD")
    currentFileCompleted = 0
    numFileCompleted = 0
    with tqdm(total=numberFileTotal, file=sys.stdout) as pbar:
        while True:
            _, numFileCompleted = combined.get()
            currentFileCompleted += numFileCompleted
            pbar.update(numFileCompleted)
            time.sleep(1)
            if currentFileCompleted == numberFileTotal:
                break
    print("COMPLETED")
    workerQueue.join()


def dashboardImageFiles(filenames, token):
    ##################################
    oldlen = len(filenames)
    filenames = checkExistenceFile(filenames=filenames, daita_token=token)
    if len(filenames) == 0:
        print("All name files are present in this project, please check them again!")
        footer()
    elif len(filenames) != oldlen:
        print(
            "Some files are already present in this project, please check them again!"
        )
        footer()
    filenames = check_size_image(filenames)
    if len(filenames) == 0:
        print("No file to upload")
        footer()
    ################################
    upload_images(filenames, token)
