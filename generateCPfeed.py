

import pandas as pd
from pandasql import sqldf

MASTER_FILE = '/home/steve/tmp/chinesepod/chinesepodLessons.xlsx'

def main():

    df = pd.read_excel(MASTER_FILE, sheet_name='all_lessons')
    # print(df)

    output = sqldf("select lessonId, title, levelShowCode, hashKey from df where dl_pdf=='y' or dl_mp3=='y' or dl_dg=='y'")
    print(output)

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
main()