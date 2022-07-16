from ast import Pass
import os
import glob
import requests
import time
from os import system, name
from upload_images import dashboardImageFiles
from upload_zip import dashboardCompressFiles
from footer import footer
from urllib.parse import urlencode

checkDaitaTokenEndpoint = "https://uflt5029de.execute-api.us-east-2.amazonaws.com/devdaitabeapp/cli/check_daita_token"


def validFileImage(filename):
    return (os.path.splitext(filename)[1]).lower() in ['.jpeg', '.png', '.jpg']


def validCompressfile(filename):
    return (os.path.splitext(filename)[1]).lower() in ['.tar', '.gz', '.bz2', '.zip']


def listImageFile(dir):
    filenames = []
    for root, subFolder, files in os.walk(dir):
        for item in files:
            if validFileImage(item):
                filenames.append(os.path.join(root, item))
    return filenames


def listCompressFile(dir):
    filenames = []
    for root, _, files in os.walk(dir):
        for item in files:
            if validCompressfile(item):
                filenames.append(os.path.join(root, item))
    return filenames


def checkDaitaToken(daita_token):
    params = {"daita_token": daita_token}
    response = requests.get(checkDaitaTokenEndpoint, params=params)
    data = response.json()
    if data['error'] == True:
        print(data['message'])
        os._exit(1)


def listAllFilesInDirectory(dir):
    imagefiles = listImageFile(dir)
    compressfiles = listCompressFile(dir)
    return imagefiles, compressfiles


def daitaLogo():
    def clear():
        if name == 'nt':
            _ = system('cls')
        else:
            _ = system('clear')
    plankspace = " "

    def printLogo(plank, num):
        with open("daita_logo_console.txt", 'r') as f:
            data = f
            for it in data:
                stringTemp = it.replace('\n', '')
                print(plank*num+stringTemp)
            time.sleep(0.5)

    clear()
    for i in reversed(range(10)):
        printLogo(plankspace, i)
        if i != 0:
            clear()


def menuSelectypeFileToUpload():
    print("Please choose mode:")
    print("0. Image file")
    print("1. Zip file")
    mode = None
    while True:
        tempMode = int(input("Select : "))
        if tempMode > 1:
            print("Invalid, please select again!")
        else:
            mode = tempMode
            break
    return mode


def dashboard(daita_token, dir):

    try:
        daitaLogo()
    except Exception as e:
        pass

    # check token
    checkDaitaToken(daita_token=daita_token)

    # check input directory
    if not os.path.isdir(dir):
        print("Please input directory path, Try it again!")
        footer()
    imagefiles, compressfiles = listAllFilesInDirectory(dir)

    if len(imagefiles) == 0 and len(compressfiles) == 0:
        print("Folder is empty, Please choose again!")
        footer()

    if len(imagefiles) > 0 and len(compressfiles) == 0:
        dashboardImageFiles(imagefiles, daita_token)
    elif len(compressfiles) > 0 and len(imagefiles) == 0:
        dashboardCompressFiles(compressfiles)
    elif len(compressfiles) > 0 and len(imagefiles) > 0:
        selectMode = menuSelectypeFileToUpload()
        if selectMode == 0:
            dashboardImageFiles(imagefiles, daita_token)
        else:
            dashboardCompressFiles(compressfiles, daita_token)
    footer()
