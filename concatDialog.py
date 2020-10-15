import pandas as pd
from pandasql import sqldf
from fileutils import FileUtil
import requests, json
import urllib
from bs4 import BeautifulSoup
import stringcase

MASTER_FILE = '/home/steve/tmp/chinesepod/chinesepodLessons.xlsx'
OUTPUT_FILE_DIR = '/home/steve/workspace/sc4933.github.io/downloads'

S3_URL = "http://s3contents.chinesepod.com/" 

def main():

    df = pd.read_excel(MASTER_FILE, sheet_name='upper_intemediate')
    df = df.head(5)

    for index, row in df.iterrows():

        url = getDialogUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])
        fpath = OUTPUT_FILE_DIR + "/" + stringcase.alphanumcase(row['title']) + ".mp3"
        urllib.request.urlretrieve(url, fpath)



def getDialogUrl(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(4)
    return S3_URL + lessonId + "/" + hashKey + "/mp3/chinesepod_" + levelShowCode + lessonId + "dg.mp3"


main()