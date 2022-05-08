import os
import glob
import time
import requests
import hashlib
import sys
import queue
import threading
from tqdm import tqdm
from itertools import chain, islice
import argparse
parser = argparse.ArgumentParser(description='Optional app description')
endpoint = 'https://nzvw2zvu3d.execute-api.us-east-2.amazonaws.com/staging/s3/presigned-url'
parser.add_argument('--dir', type=str,
                    help='A required integer positional argument')
parser.add_argument('--identity_id', type=str,
                    help='A required integer positional argument')  
parser.add_argument('--project_id', type=str,
                    help='A required integer positional argument')  
parser.add_argument('--id_token', type=str,
                    help='A required integer positional argument')  
parser.add_argument('--project_name', type=str,
                    help='A required integer positional argument')    
args = parser.parse_args()           
dir = args.dir
identity_id = args.identity_id
project_id = args.project_id
id_token = args.id_token
project_name = args.project_name
batch_size = 10
def batcher(iterable, size):
    iterator = iter(iterable)
    for first in iterator:
        yield list(chain([first], islice(iterator, size - 1)))

def getPresignUrl(filesnames):
    filenamesDict = {os.path.basename(it): it for it in filesnames}
    filenamesList = []
    ls_object_info = []
    for it in filesnames:
        with open (it,'rb') as f:
            hash = hashlib.md5(f.read()).hexdigest()
        temp =    {
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
        'filenames':filenamesList,
        'identity_id': identity_id,
        'project_id': project_id,
        'id_token': id_token,
        'ls_object_info': ls_object_info,
        'project_name': project_name
    }
    preSignUrlResp = requests.post(endpoint,json=payload)
    preSignUrlResult = preSignUrlResp.json()['data']
    for k , v in filenamesDict.items():
        files ={'file': open(v,'rb')}
        requests.post(preSignUrlResult[k]['url'],data=preSignUrlResult[k]['fields'],files=files)
def generator():
    yield from glob.glob(dir+'/*')

class ThreadWorker(threading.Thread):
    def __init__(self,queue,updateQueue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.updateQueue = updateQueue
    def run(self):
        while True:
            filenames = self.queue.get()
            getPresignUrl(filesnames=filenames)
            self.updateQueue.put(len(filenames))
            self.queue.task_done()


def main():
    batches = [it for it in batcher(generator(),batch_size)]
    workerQueue =  queue.Queue()
    updateProcessbarQueue = queue.Queue()
    for batch in batches:
        workerQueue.put(batch)

    for i in range(5):
        t = ThreadWorker(queue=workerQueue,updateQueue=updateProcessbarQueue)
        t.setDaemon(True)
        t.start()
    
    combined = queue.Queue(maxsize=0)
    def listen(q):
        while True:
            combined.put((q,q.get()))
    t1 = threading.Thread(target=listen,args=(updateProcessbarQueue,))
    t1.daemon =True 
    t1.start()
    workerQueue.join()
    numberFileTotal = len(glob.glob(dir+'/*'))
    currentNumberFiles = 0
    print("STARTING UPLOAD")
    with tqdm(total=numberFileTotal, file=sys.stdout) as pbar:
        numFileCompleted = 0
        while True:
            _,numFileCompleted = combined.get()
            break
        pbar.update(numberFileTotal)
    print("COMPLETED")