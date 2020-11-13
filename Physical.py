from moviepy.editor import VideoFileClip
# Standard PySceneDetect imports:
from scenedetect import VideoManager
from scenedetect import SceneManager

# For content-aware scene detection:
from scenedetect.detectors import ContentDetector
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
def get_physical_feature(video_files,start,ss,ee):
    data = []
    for i in range(ss,ee):
        try:
            path = video_files[i]
            if not path.endswith('mp4'):
                continue
            #print(i, "/", e-s)
            video_id = path.split('/')[-1][:-4]
            # video_id = path[:-4]
            foreground_area, mag_, ang_, cob_, clarity_per, bright, warm, sat_ = get_aesthetic_features(path)
            onedata = [video_id, foreground_area, mag_, ang_, warm, sat_, bright, cob_, clarity_per]
            data.append(onedata)
        except Exception as e:
            print(e)
            name = 'results/%d_%d_physica_feature_%d.csv'%(500*start+ss,500*start+ee, i)
            table = pd.DataFrame(data=data, columns=['id', 'ForegroundMotionArea', 'MotionMagnitude', 'MotionDirection',
                                                     'WarmHueProportion', 'Saturation', 'Brightness', 'CoB', 'Clarity'])
            table.to_csv(name)
            print("csv saved to %s" % name)
    table = pd.DataFrame(data=data, columns=['id', 'ForegroundMotionArea', 'MotionMagnitude', 'MotionDirection',
                                             'WarmHueProportion', 'Saturation', 'Brightness', 'CoB', 'Clarity'])
    table.to_csv('results/%d_%d_physical.csv' %(500*start+ss,500*start+ee))
    print("---get physical feature")

def get_aesthetic_features(path):
    backSub = cv.createBackgroundSubtractorKNN()
    capture = cv.VideoCapture(cv.samples.findFile(path))
    ret, frame = capture.read()
    # fgMask = backSub.apply(frame) #fgmask前景不等于1
    prvs = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame)
    hsv[..., 1] = 255
    Mag = []
    Ang = []
    foreground = []
    count = 0
    Brightness = []
    Cob = []
    Clarity = []
    Warm = []
    Sat = []
    while (count < 500):
        count += 1
        ret, frame2 = capture.read()
        if count < 100:
            continue
        # foreground
        fgMask = backSub.apply(frame2)
        fgmask_pro = (0 < fgMask).sum() / fgMask.size
        # warm_color
        hsv = cv.cvtColor(frame2, cv.COLOR_BGR2HSV)
        lower_warm = np.array([0, 43, 46])
        upper_warm = np.array([35, 255, 255])
        mask = cv.inRange(hsv, lower_warm, upper_warm)
        lower_warm = np.array([125, 43, 46])
        upper_warm = np.array([180, 255, 255])
        mask2 = cv.inRange(hsv, lower_warm, upper_warm)
        mask = mask + mask2
        warm_pro = (mask != 0).sum() / mask.size
        Warm.append(warm_pro)
        # print(warm_pro)
        # others
        sat = np.mean(hsv[..., 1]) / 255
        Sat.append(sat)
        value = hsv[..., 2] / 255
        brightness = np.mean(value)
        cob = np.std(value)
        min_max_scaler = preprocessing.MinMaxScaler()
        clarity = min_max_scaler.fit_transform(value)
        clarity_pro = (0.7 < clarity).sum() / clarity.size
        # print(clarity_pro)
        Clarity.append(clarity_pro)
        Cob.append(cob)
        Brightness.append(brightness)
        foreground.append(fgmask_pro)
        next = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)
        flow = cv.calcOpticalFlowFarneback(prvs, next, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        mag, ang = cv.cartToPolar(flow[..., 0], flow[..., 1])
        angg = np.average(ang)
        magg = np.average(cv.normalize(mag, None, 0, 255, cv.NORM_MINMAX))
        Mag.append(magg)
        Ang.append(angg)
        # print(magg)
        # print(magg,angg)
        # print(ang)
        # print(cv.normalize(mag,None,0,1,cv.NORM_MINMAX))
        # break
        prvs = next
    foreground_area = np.average(foreground)
    mag_ = np.nanmean(Mag)
    ang_ = np.average(Ang)
    cob_ = np.mean(Cob)
    clarity_per = np.mean(Clarity)
    bright = np.mean(Brightness)
    warm = np.mean(Warm)
    sat_ = np.mean(Sat)
    return foreground_area, mag_, ang_, cob_, clarity_per, bright, warm, sat_