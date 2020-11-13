import pandas as pd
import numpy as np
from Audio import *
from Physical import *
from Sentiment import *
from Emotion import *
import glob
import os
from multiprocessing import Process, Manager
import shutil
import pexpect


def download(file,start):
    df = pd.read_csv(file)
    for i in range(start,start+1):
        df.loc[i * 500:(i + 1) * 500, ['video_id']].to_csv(str(i) + '.txt', header=None, sep=' ', index=None)
    cmd = 'youtube-dl -a %d.txt --id -f best -i'%start
    os.system(cmd)
    print('---download complete')
    lst = glob.glob('*.mp4*')
    for i in range(len(lst)):
        try:
            f = lst[i]
            dstfile = "video/video%d/%s" %(start,str(f))
            mycopyfile(f, dstfile)
            os.remove(f)
        except Exception as e:
            print(e)
    print('---transfer complete')
    if not os.path.exists(savepath):
        os.makedirs(savePath)
        
def transfer(start):
    name = ['video','subtitle','image','audio']
    for transfer_name in name:
        cmd = "scp -r %s/%s%d -P 22 macheng@bridges.psc.xsede.org:/pylon5/sbe200006p/macheng/youtube_%s"%(transfer_name,transfer_name,start,transfer_name)
        if transfer_name == 'video':
            cmd += 's'
        os.system(cmd)
        p = subprocess.Popen(cmd.split(' '),stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = p.communicate(input='CMJ18684655366mmm\n')
        del_file('%s/%s%d'%(transfer_name,transfer_name,start))

def process(video_files,start,s,e):
    #get_emotional_feature(video_files,start,s,e)
    #get_sentiment_feature(video_files,start,s,e)
    #get_physical_feature(video_files,start,s,e)
    #get_audio_feature(video_files,start,s,e)
    
    
        
def mycopyfile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print ("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件
        print ("copy %s -> %s"%( srcfile,dstfile))
        
def del_file(path):
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            del_file(c_path)
        else:
            os.remove(c_path)
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))       
        
if __name__ == '__main__':
    savepath = 'results/'
    start = 5
    influencers_info = 'channelid_video_ids_for_downloading.csv'
    #download(influencers_info,start)
    numOfProcesses = 10
    numOfGroup = 500
    termsPerProc = int(numOfGroup * 1.0/numOfProcesses)
    mgr = Manager()
    output_file = []
    #for i in range(numOfProcesses):
    #    output_file.append(f_term_semnet_features+str(i)+'.txt')
    video_file_lst = glob.glob('video/video%d/*.mp4*'%start)
    jobs = []
    for i in range(numOfProcesses):
        if i == numOfProcesses - 1:
            p = Process(target=process, args=(video_file_lst,start, i*termsPerProc, len(video_file_lst)))
        else:
            p = Process(target=process, args=(video_file_lst,start, i*termsPerProc, (i+1)*termsPerProc))
        jobs.append(p)
        p.start()
        #p.join()
    for proc in jobs:
        proc.join()
    transfer(start)