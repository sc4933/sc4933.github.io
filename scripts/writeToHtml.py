import pandas as pd
from pandasql import sqldf
from fileutils import FileUtil
import requests, json
import urllib
from bs4 import BeautifulSoup
import stringcase

# globals
MASTER_FILE = '/home/steve/tmp/chinesepod/chinesepodLessons.xlsx'
OUTPUT_FILE_DIR = '/home/steve/workspace/sc4933.github.io/'
S3_URL = "http://s3contents.chinesepod.com/" 



# configs
SHEET_NAME = '2020-10-17-206-479'

def main():

    df = pd.read_excel(MASTER_FILE, sheet_name=SHEET_NAME)
    df = sqldf("select * from df")   
    print(df)

    # create html page (using pdf selected DF)
    df['MP3'] = df.apply (lambda row: hyperlink(getMp3Url(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)
    df['Dialog'] = df.apply (lambda row: hyperlink(getDialogUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)
    df['PDF'] = df.apply (lambda row: hyperlink(getPdfUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)

    # clean up columns and create html page
    del df['hashKey']
    FileUtil.saveToFile(df.to_html(escape=False), OUTPUT_FILE_DIR + 'cp.html') 


'''
    Helpers
'''
def hyperlink(url):
    return '<a href=' + url + '><div>link</div></a>'


def generateItem(title, url):
    fileType = 'audio/mpeg' if url.endswith('.mp3') else 'application/pdf'
    return "<item> <title> %s </title> <enclosure url='%s' type='%s' /> </item>" % (title, url, fileType)


def getMp3Url(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(4)
    return S3_URL + lessonId + "/" + hashKey + "/mp3/chinesepod_" + levelShowCode + lessonId + "pb.mp3"

def getDialogUrl(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(4)
    return S3_URL + lessonId + "/" + hashKey + "/mp3/chinesepod_" + levelShowCode + lessonId + "dg.mp3"

def getPdfUrl(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(4)
    return S3_URL + lessonId + "/" + hashKey + "/pdf/chinesepod_" + levelShowCode + lessonId + ".pdf"


'''
    can be ignored
'''
BOILERPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>%s</title>
%s
  </channel>
</rss>

    """

main()