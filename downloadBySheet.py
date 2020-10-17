import pandas as pd
from pandasql import sqldf
from fileutils import FileUtil
import requests, json
import urllib
from bs4 import BeautifulSoup
import stringcase

# globals
MASTER_FILE = '/home/steve/tmp/chinesepod/chinesepodLessons.xlsx'
OUTPUT_FILE_DIR = '/home/steve/workspace/sc4933.github.io/downloads'
S3_URL = "http://s3contents.chinesepod.com/" 

# configs
SHEET_NAME = '2020-10-17-206-479'

def main():

    df = pd.read_excel(MASTER_FILE, sheet_name=SHEET_NAME)
    df = sqldf("select * from df")   
    print(df)

    for index, row in df.iterrows():

        filename = stringcase.alphanumcase(row['title']) + ".mp3"
        print("%s: downloading %s"  % (index, filename))
        
        try:
            url = getDialogUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])
            fpath = OUTPUT_FILE_DIR + "/" + filename
            urllib.request.urlretrieve(url, fpath)
        except:
            print('error download ' + filename)



def getDialogUrl(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(4)
    return S3_URL + lessonId + "/" + hashKey + "/mp3/chinesepod_" + levelShowCode + lessonId + "dg.mp3"


main()