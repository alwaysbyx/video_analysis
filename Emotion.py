import urllib.request
import urllib.error
import time
import os
import pandas as pd
import glob
import urllib
#import urllib2 
import time
import json
import glob
from tqdm import tqdm
import numpy as np
import cv2 as cv
import time
from sklearn import preprocessing

def get_emotional_feature(video_files,start,ss,ee):
    data = []
    scene = []
    false_count = []
    i = ss
    try:
        if not os.path.isdir('image/image%d'%start):
            os.makedirs("image/image%d" %start)
        for i in range(ss,ee):
            p = video_files[i]
            if not p.endswith('mp4'):
                continue
            video_id = p.split('/')[-1][:-4]
            video_img_path = "image/image%d/%s" % (start, video_id)
            # img_lst = glob.glob(video_img)
            print(i, "/", ee-ss)
            if os.path.isdir(video_img_path)==False:
                cd = "scenedetect -i '%s' -o 'image/image%d/%s/' detect-content -t 30 save-images -n 1" % (str(p), int(start), str(video_id))
                os.system(cd)
            count = 0
            scene_num = len(get_all_path(video_img_path))
            scene.append([video_id, scene_num])
            if len(get_all_path(video_img_path)) > 0:
                for imgpath in get_all_path(video_img_path):
                    if ifpeople(imgpath) == True:
                        try:
                            od, face_sum = detect(imgpath)
                            for i in range(face_sum):
                                onedata = [ele[i] for ele in od]
                                onedata.append(video_id)
                                onedata.append(imgpath)
                                onedata.append(face_sum)
                                onedata.append(i)
                                data.append(onedata)
                            count += 1
                        except Exception as e:
                            print(e)
            print(video_id, "has %d faces detected" % (count))
            # del_file('image/%s/'%(video_id))
            if count == 0:
                false_count.append(video_id)
        table = pd.DataFrame(data=data,
                             columns=['gender', 'age', 'smile', 'anger', 'disgust', 'fear', 'happiness', 'neutral',
                                      'sadness', 'surprise', 'facequality', 'beauty_female', 'beauty_male',
                                      'skin_status_health', 'skin_status_stain', 'skin_status_darkcircle',
                                      'skin_status_acne', 'glass', 'blurness', 'motionblur', 'gaussianblur',
                                      'ethnicity', 'id', 'time', 'face_sum', 'face_n'])
        table.to_csv('results/%d_%d_emotion.csv' % (500*start+ss,500*start+ee))
        table = pd.DataFrame(data=scene, columns=['id', 'scene_num'])
        table.to_csv('results/%d_%d_scene.csv' %(500*start+ss,500*start+ee))
    except Exception as e:
        name = 'results/%d_%d_emotion_%d.csv'%(500*start+ss,500*start+ee, i)
        table = pd.DataFrame(data=data,
                             columns=['gender', 'age', 'smile', 'anger', 'disgust', 'fear', 'happiness', 'neutral',
                                      'sadness', 'surprise', 'facequality', 'beauty_female', 'beauty_male',
                                      'skin_status_health', 'skin_status_stain', 'skin_status_darkcircle',
                                      'skin_status_acne', 'glass', 'blurness', 'motionblur', 'gaussianblur',
                                      'ethnicity', 'id', 'time', 'face_sum', 'face_n'])
        table.to_csv(name)
    table = pd.DataFrame(data=false_count, columns=["no_emotion_id"])
    table.to_csv('results/%d_%d_false.csv' %(500*start+ss,500*start+ee))
'''
def get_emotional_feature(video_files,start,ss,ee):
    data = [1,2,3]
    e = ee
    s = ss
    table = pd.DataFrame(data=data, columns=["no_emotion_id"])
    table.to_csv('%d_%d_false.csv' %(500*start+s,500*start+e))
'''
def mycopyfile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print ("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件
        print ("copy %s -> %s"%( srcfile,dstfile))
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

def detect(imgpath):
    http_url = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
    key = "jZdxCpRYU-DicN5sCmGpTBMiDx266RZW"
    secret = "rkOZ5THsPj22x6dF9-oZIXugraqr2Dyz"
    filepath = imgpath
    #print(filepath)
    #print(ifpeople(filepath))
    boundary = '----------%s' % hex(int(time.time() * 1000))
    data = []
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_key')
    data.append(key)
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'api_secret')
    data.append(secret)
    data.append('--%s' % boundary)
    fr = open(filepath, 'rb')
    data.append('Content-Disposition: form-data; name="%s"; filename=" "' % 'image_file')
    data.append('Content-Type: %s\r\n' % 'application/octet-stream')
    data.append(fr.read())
    fr.close()
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_landmark')
    data.append('1')
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"\r\n' % 'return_attributes')
    data.append(
        "gender,age,smiling,headpose,facequality,blur,eyestatus,emotion,ethnicity,beauty,mouthstatus,eyegaze,skinstatus")
    data.append('--%s--\r\n' % boundary)

    for i, d in enumerate(data):
        if isinstance(d, str):
            data[i] = d.encode('utf-8')

    http_body = b'\r\n'.join(data)

    # build http request
    req = urllib.request.Request(url=http_url, data=http_body)

    # header
    req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)

    try:
        # post data to server
        resp = urllib.request.urlopen(req, timeout=30)
        # get response
        qrcont = resp.read()
        # if you want to load as json, you should decode first,
        # for example: json.loads(qrount.decode('utf-8'))
        dict = eval(qrcont)
        faces = dict["faces"]
        gender = []
        age = []
        smile = []
        anger =[]
        disgust=[]
        fear=[]
        happiness=[]
        neutral=[]
        sadness=[]
        surprise=[]
        facequality=[]
        beauty_female=[]
        beauty_male=[]
        skin_status_health=[]
        skin_status_stain=[]
        skin_status_darkcircle=[]
        skin_status_acne=[]
        glass=[]
        blurness = []
        motionblur = []
        gaussianblur = []
        ethnicity = []
        #idd = []
        #video_id = filepath.split('/')[-1][:-4]
        for i in range(len(faces)):
            attr = faces[i]["attributes"]
            #idd.append(video_id)
            gender.append(attr["gender"]["value"])
            age.append(attr["age"]["value"])
            smile.append(attr["smile"]["value"])
            anger.append(attr["emotion"]["anger"])
            disgust.append(attr["emotion"]["disgust"])
            fear.append(attr["emotion"]["fear"])
            happiness.append(attr["emotion"]["happiness"])
            neutral.append(attr["emotion"]["neutral"])
            sadness.append(attr["emotion"]["sadness"])
            surprise.append(attr["emotion"]["surprise"])
            facequality.append(attr["facequality"]["value"])
            beauty_female.append(attr["beauty"]["female_score"])
            beauty_male.append(attr["beauty"]["male_score"])
            skin_status_health.append(attr["skinstatus"]["health"])
            skin_status_stain.append(attr["skinstatus"]["stain"])
            skin_status_darkcircle.append(attr["skinstatus"]["dark_circle"])
            skin_status_acne.append(attr["skinstatus"]["acne"])
            glass.append(attr["glass"]["value"])
            blurness.append(attr["blur"]["blurness"]["value"])
            motionblur.append(attr["blur"]["motionblur"]["value"])
            gaussianblur.append(attr["blur"]["gaussianblur"]["value"])
            ethnicity.append(attr["ethnicity"]["value"])
            
        onedata = [gender,age,smile,anger,disgust,fear,happiness,neutral,sadness,surprise,facequality,beauty_female,beauty_male,skin_status_health,skin_status_stain,skin_status_darkcircle,skin_status_acne,glass,blurness,motionblur,gaussianblur,ethnicity]
        return onedata,len(faces)
        #print(onedata)
    except urllib.error.HTTPError as e:
        print(e.read().decode('utf-8'))
def ifpeople(image_path,show=False):
    try:
        #img = Image.open(urlopen(newurl))
        face_cascade = cv.CascadeClassifier(cv.haarcascades+'haarcascade_frontalface_alt2.xml')
        # 读取图片，并获得灰度图
        image = cv.imread(image_path)
        gray = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
        if show==True:
            plt.imshow(image)
        # 检测人脸，返回人脸的坐标
        faces = face_cascade.detectMultiScale(gray,scaleFactor=1.15,minNeighbors=5,minSize=(5,5))
        if len(faces) > 0:
            return True
        '''
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        if face_locations:
            return True
            '''
        return False
    except Exception as e:
        print(e)
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