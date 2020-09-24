import pandas as pd
from pandasql import sqldf
from fileutils import FileUtil

MASTER_FILE = '/home/steve/tmp/chinesepod/chinesepodLessons.xlsx'
OUTPUT_FILE = '/home/steve/workspace/sc4933.github.io/cpfeed.xml'

S3_URL = "http://s3contents.chinesepod.com/" 

def main():

    # df = pd.read_excel(MASTER_FILE, sheet_name='all_lessons')
    # # print(df)

    # output = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_pdf=='y' or dl_mp3=='y' or dl_dg=='y'")
    # print(output)

    lessonId = 2369.000
    title = 'Giving Red Envelopes'
    levelShowCode = 'C'
    hashKey = 'e2ff74e47e7d91a8701dbeae5819dd8805312af6'

    print( getMp3Url(lessonId, levelShowCode, hashKey) )
    print( getDialogUrl(lessonId, levelShowCode, hashKey) )
    print( getPdfUrl(lessonId, levelShowCode, hashKey) )
    print( generateItem(title, getPdfUrl(lessonId, levelShowCode, hashKey)) )

    # create item list
    itemList = generateItem(title, getPdfUrl(lessonId, levelShowCode, hashKey))

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