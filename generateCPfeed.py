import pandas as pd
from pandasql import sqldf
from fileutils import FileUtil

MASTER_FILE = '/home/steve/tmp/chinesepod/chinesepodLessons.xlsx'
OUTPUT_FILE = '/home/steve/workspace/sc4933.github.io/cpfeed.xml'

S3_URL = "http://s3contents.chinesepod.com/" 

def main():

    df = pd.read_excel(MASTER_FILE, sheet_name='all_lessons')
    itemList = ''

    # add mp3 lessons
    filteredDf = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_mp3=='y'")   
    for index, row in filteredDf.iterrows():
        itemList += generateItem(row['title'], getMp3Url(row['lessonId'], row['levelShowCode'], row['hashKey'])) +"\n"


    # add dialog lessons
    filteredDf = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_dg=='y'")   
    for index, row in filteredDf.iterrows():
        itemList += generateItem(row['title'] + "(dg)", getDialogUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])) +"\n"

    # add pdf lessons
    filteredDf = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_pdf=='y'")   
    for index, row in filteredDf.iterrows():
        itemList += generateItem(row['title'] + "(pdf)", getPdfUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])) +"\n"


    # insert itemList into boilerplate
    boilerplate = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>CP Feed</title>
%s
  </channel>
</rss>

    """ % itemList

    
    # save feed
    FileUtil.saveToFile(boilerplate, OUTPUT_FILE)




def generateItem(title, url):
    fileType = 'audio/mpeg' if url.endswith('.mp3') else 'application/pdf'
    return "<item> <title> %s </title> <enclosure url='%s' type='%s' /> </item>" % (title, url, fileType)


def getMp3Url(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(3)
    return S3_URL + lessonId + "/" + hashKey + "/mp3/chinesepod_" + levelShowCode + lessonId + "pb.mp3"

def getDialogUrl(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(3)
    return S3_URL + lessonId + "/" + hashKey + "/mp3/chinesepod_" + levelShowCode + lessonId + "dg.mp3"

def getPdfUrl(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(3)
    return S3_URL + lessonId + "/" + hashKey + "/pdf/chinesepod_" + levelShowCode + lessonId + ".pdf"

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
main()