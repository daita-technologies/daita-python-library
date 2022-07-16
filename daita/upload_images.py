import os
import glob
import time
import requests
import hashlib
import sys
import queue
import threading
from tqdm import tqdm
from footer import footer
from itertools import chain, islice
batch_size = 10
###### the endpoint for dev enviroment#######################################################################################
endpointPresignURL = 'https://uflt5029de.execute-api.us-east-2.amazonaws.com/devdaitabeapp/cli/upload_project'
endpointCheckExistenceFile = 'https://uflt5029de.execute-api.us-east-2.amazonaws.com/devdaitabeapp/cli/check_existence_file'
#############################################################################################################################

daita_token = None


def batcher(iterable, size):
    iterator = iter(iterable)
    for first in iterator:
        yield list(chain([first], islice(iterator, size - 1)))


def getPresignUrl(filesnames):
    filenamesDict = {os.path.basename(it): it for it in filesnames}
    filenamesList = []
    ls_object_info = []
    for it in filesnames:
        with open(it, 'rb') as f:
            hash = hashlib.md5(f.read()).hexdigest()
        temp = {
            "s3_key": "",
            "filename": os.path.basename(it),
            "hash": hash,
            "size": os.path.getsize(it),
            "is_ori": True,
            "gen_id": ""
        }
        filenamesList.append(os.path.basename(it))
        ls_object_info.append(temp)

    payload = {
        'filenames': filenamesList,
        'ls_object_info': ls_object_info,
        'daita_token': daita_token
    }
    preSignUrlResp = requests.post(endpointPresignURL, json=payload)
    if preSignUrlResp.status_code != 200:
        print("Something Wrong, please check again")
        print(preSignUrlResp.text)
        footer()
    if preSignUrlResp.json()['error'] == True:
        print("Something Wrong, please check again")
        print(preSignUrlResp.json()['message'])
        footer()

    preSignUrlResult = preSignUrlResp.json()['data']
    for k, v in filenamesDict.items():
        files = {'file': open(v, 'rb')}
        requests.post(
            preSignUrlResult[k]['url'], data=preSignUrlResult[k]['fields'], files=files)


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
            getPresignUrl(filesnames=filenames)
            self.updateQueue.put(len(filenames))
            self.queue.task_done()


def checkExistenceFile(filenames, daita_token):

    fullfile = {os.path.basename(it): it for it in filenames}
    basenamefilenames = [os.path.basename(it) for it in filenames]

    payload = {
        'ls_filename': basenamefilenames,
        'daita_token': daita_token
    }

    RespcheckExistenceFile = requests.post(
        endpointCheckExistenceFile, json=payload)

    ResultcheckExistenceFile = RespcheckExistenceFile.json()
    if ResultcheckExistenceFile['error'] == True:
        print(f"Something wrong with {ResultcheckExistenceFile['message']}")
        os._exit(1)

    if len(ResultcheckExistenceFile['data']) == 0:
        return filenames
    newFileNotExist = []

    for it in ResultcheckExistenceFile['data']:
        if it['filename'] in fullfile:
            del fullfile[it['filename']]

    for k, v in fullfile.items():
        newFileNotExist.append(v)
    return newFileNotExist


def check_size_image(filenames):
    oldlen = len(filenames)
    newArr = list(filter(lambda x: int(
        os.path.getsize(x)/(1024**2)) <= 5, filenames))
    if oldlen != len(newArr):
        print("Some files are larger than 5 MB")
    return newArr


def upload_images(filenames, token):
    global daita_token
    daita_token = token
    batches = [it for it in batcher(generator(filenames), batch_size)]
    workerQueue = queue.Queue()
    updateProcessbarQueue = queue.Queue()
    for batch in batches:
        workerQueue.put(batch)

    for _ in range(5):
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
    workerQueue.join()
    numberFileTotal = len(filenames)
    print(f'Total File: {numberFileTotal}')
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


def dashboardImageFiles(filenames, token):
    ##################################
    oldlen = len(filenames)
    filenames = checkExistenceFile(
        filenames=filenames, daita_token=token)
    if len(filenames) == 0:
        print("All name file is existed on this project, please check again!")
        footer()
    elif len(filenames) != oldlen:
        print("Some files is existed on this project, now just others!")
    filenames = check_size_image(filenames)
    if len(filenames) == 0:
        print("No file to upload")
        footer()
    ################################
    upload_images(filenames, token)
