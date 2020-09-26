import pandas as pd
from pandasql import sqldf
from fileutils import FileUtil

MASTER_FILE = '/home/steve/tmp/chinesepod/chinesepodLessons.xlsx'
OUTPUT_FILE_DIR = '/home/steve/workspace/sc4933.github.io/'

S3_URL = "http://s3contents.chinesepod.com/" 

BOILERPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>%s</title>
%s
  </channel>
</rss>

    """

def main():

    df = pd.read_excel(MASTER_FILE, sheet_name='all_lessons')

    # mp3 feed
    itemList = ''
    filteredDf = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_mp3=='y'")   
    for index, row in filteredDf.iterrows():
        itemList += generateItem(row['title'], getMp3Url(row['lessonId'], row['levelShowCode'], row['hashKey'])) +"\n"

    FileUtil.saveToFile(BOILERPLATE % ('CP MP3', itemList), OUTPUT_FILE_DIR + 'cp.xml')

    # dialog feed
    itemList = ''
    filteredDf = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_dg=='y'")   
    for index, row in filteredDf.iterrows():
        itemList += generateItem(row['title'] + "(dg)", getDialogUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])) +"\n"

    FileUtil.saveToFile(BOILERPLATE % ('CP Dialog', itemList), OUTPUT_FILE_DIR + 'cpdg.xml')

    # pdf feed
    itemList = ''
    filteredDf = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_pdf=='y'")   
    for index, row in filteredDf.iterrows():
        itemList += generateItem(row['title'] + "(pdf)", getPdfUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])) +"\n"

    FileUtil.saveToFile(BOILERPLATE % ('CP PDF', itemList), OUTPUT_FILE_DIR + 'cppdf.xml')

    # create html page
    filteredDf['MP3'] = filteredDf.apply (lambda row: hyperlink(getMp3Url(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)
    filteredDf['Dialog'] = filteredDf.apply (lambda row: hyperlink(getDialogUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)
    filteredDf['PDF'] = filteredDf.apply (lambda row: hyperlink(getPdfUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)
    del filteredDf['lessonId']
    del filteredDf['levelShowCode']
    del filteredDf['hashKey']

    FileUtil.saveToFile(BOILERPLATE % ('CP PDF', itemList), OUTPUT_FILE_DIR + 'cppdf.xml') 

    print(filteredDf)
    FileUtil.saveToFile(filteredDf.to_html(escape=False), OUTPUT_FILE_DIR + 'cp.html') 


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

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
main()