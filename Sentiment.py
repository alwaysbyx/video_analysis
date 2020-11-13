import os
import re
from textblob import TextBlob
import glob
import numpy as np
import pandas as pd
def get_sentiment_feature(video_files,start,ss,ee):
    data = []
    output =  "subtitles/subtitle%d"%start
    if not os.path.isdir(output):
        os.makedirs(output)
    for i in range(ss,ee):
        f = video_files[i]
        if not f.endswith('.mp4'):
            continue
        video_id = f.split('/')[-1][:-4]
        output_sub = "subtitle/subtitle%d/%s.srt"%(start,video_id)
        if not os.path.isfile(output_sub):
            cd = "autosub %s -o %s" % (str(f),output_sub)
            os.system(cd)
        text = srt2txt(output_sub)
        blob = TextBlob(text)
        sentiment = []
        words = len(blob.words)
        for sentence in blob.sentences:
            sentiment.append(sentence.sentiment.polarity)
        onedata = [video_id, np.mean(sentiment), words]
        data.append(onedata)
        # print(words)
        # os.remove(f)
    table = pd.DataFrame(data=data, columns=['id', 'sentiment', 'words'])
    table.to_csv('results/%d_%d_sentiment.csv' %(500*start+ss,500*start+ee))

def srt2txt(srtfile):
    # read file line by line
    file = open(srtfile, "r")
    lines = file.readlines()
    file.close()

    text = ''
    for line in lines:
        if re.search('^[0-9]+$', line) is None and re.search('^[0-9]{2}:[0-9]{2}:[0-9]{2}', line) is None and re.search('^$', line) is None:
            text += ' ' + line.rstrip('\n')
        text = text.lstrip()
    return(text)

def get_all_path(open_file_path):
    rootdir = open_file_path
    path_list = []
    lst = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(lst)):
        com_path = os.path.join(rootdir, lst[i])
        #print(com_path)
        if os.path.isfile(com_path):
            path_list.append(com_path)
        if os.path.isdir(com_path):
            path_list.extend(get_all_path(com_path))
    #print(path_list)
    return path_list

