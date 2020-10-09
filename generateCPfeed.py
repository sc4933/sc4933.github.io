import pandas as pd
from pandasql import sqldf
from fileutils import FileUtil
import requests, json
from bs4 import BeautifulSoup

MASTER_FILE = '/home/steve/tmp/chinesepod/chinesepodLessons.xlsx'
OUTPUT_FILE_DIR = '/home/steve/workspace/sc4933.github.io/'

S3_URL = "http://s3contents.chinesepod.com/" 
ANKI_ENDPOINT = 'http://localhost:8765'

BOILERPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>%s</title>
%s
  </channel>
</rss>

    """

# configs
UPLOAD_TO_ANKI = True
ANKI_DECK_NAME = 'wechat'

def main():

    print("> generating cp feed")

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
    filteredDf = sqldf("select lessonId, studied, dl_vocab, title, levelShowCode, hashKey from df where studied='y' or dl_vocab='y' or dl_pdf=='y' order by studied desc")   
    for index, row in filteredDf.iterrows():
        itemList += generateItem(row['title'] + "(pdf)", getPdfUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])) +"\n"

    filteredDf.fillna("",inplace=True)
    # print(filteredDf)

    FileUtil.saveToFile(BOILERPLATE % ('CP PDF', itemList), OUTPUT_FILE_DIR + 'cppdf.xml')

    # create html page (using pdf selected DF)
    filteredDf['MP3'] = filteredDf.apply (lambda row: hyperlink(getMp3Url(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)
    filteredDf['Dialog'] = filteredDf.apply (lambda row: hyperlink(getDialogUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)
    filteredDf['PDF'] = filteredDf.apply (lambda row: hyperlink(getPdfUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])), axis=1)

    # clean up columns and create html page
    del filteredDf['hashKey']
    FileUtil.saveToFile(filteredDf.to_html(escape=False), OUTPUT_FILE_DIR + 'cp.html') 

    # anki vocab
    if UPLOAD_TO_ANKI:

        # create deck
        addDeck(ANKI_DECK_NAME)

        itemList = ''
        filteredDf = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_vocab=='y'")   
        # print(filteredDf)

        # send vocab to anki
        filteredDf.apply(lambda row: sendVocabToAnki(row, ANKI_DECK_NAME), axis=1)




def sendVocabToAnki(row, deckname):

    # print(row)

    htmlUrl =  getHtmlUrl(row['lessonId'], row['levelShowCode'], row['hashKey'])
    df = getVocabDf( htmlUrl )

    for index, row in df.iterrows():
        front = row['hanzi']
        back = row['pinyin'] + " - " + row['meaning']
        addNotes(deckname, front, back)

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

def getHtmlUrl(lessonId, levelShowCode, hashKey):
    lessonId = str(int(lessonId)).zfill(4)
    return S3_URL + lessonId + "/" + hashKey + "/pdf/chinesepod_" + levelShowCode + lessonId + ".html"

def getVocabDf(htmlUrl):

    r = requests.get(url=htmlUrl)
    soup = BeautifulSoup(r.text, 'html.parser')
    table = soup.find('h1', text='Key Vocabulary').find_next_sibling()
    df = pd.read_html(str(table))[0]
    df.columns = ['hanzi', 'pinyin', 'meaning']
    return df

def addDeck(deckName):

    payload = {
        "action": "createDeck",
        "params": {"deck": deckName},
        "version": 6
    }

    r = requests.post(url=ANKI_ENDPOINT, data=json.dumps(payload))
    res = json.loads(r.text)
    print(res)

    return res

def addNotes(deckName, front, back):

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deckName,
                "modelName": "Basic",
                "fields": {
                    "Front": front,
                    "Back": back
                },
                "options": {
                    "allowDuplicate": False,
                    "duplicateScope": "deck"
                },
            }
        }
    }

    r = requests.post(url=ANKI_ENDPOINT, data=json.dumps(payload))
    res = json.loads(r.text)
    print(res)



pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.0f' % x)
# pd.options.display.float_format = '{:,.0f}'.format
main()