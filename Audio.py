import os
import pandas as pd
import subprocess
import numpy as np
from moviepy.editor import *

def get_audio_feature(video_files,start,ss,ee):
    data = []
    output = 'audio/audio%d'%start
    if not os.path.isdir(output):
        os.makedirs(output)
    for i in range(ss,ee):
        file = video_files[i]
        if not file.endswith('.mp4'):
            continue
        video_id = file.split('/')[-1][:-4]
        #print(file,video_id)
        #print(file)
        outputfile = 'audio/audio%d/%s.wav'%(start,video_id)
        if not os.path.isfile(outputfile):
            video = VideoFileClip(file)
            audio = video.audio
            audio.write_audiofile(outputfile)
        wave_file = outputfile
        if not wave_file.endswith('.wav'):
            continue
        feature_file = wave_file[:-4]+'.csv'
        #print(feature_file)
        opensmile_f = OpenSmileFeatureSet(wave_file)
        feat = opensmile_f.get_IS09(feature_file)
        data.append(feat)
    table = pd.DataFrame(data=data)
    table.to_csv('results/%d_%d_audio.csv'%(500*start+ss,500*start+ee))
    print('---get audio feature complete')
        
class OpenSmileFeatureSet:
    
    def __init__(self, input_file):
        """
        初始化
        :param input_file: 输入.wav音频文件，或是openSMILE所支持的文件格式
        """

        self.openSmile_path = "opensmile/build/progsrc/smilextract/"
        self.input_file = input_file
        self.IS09_emotion = "opensmile/config/emobase/emobase.conf"

    def feature_extraction(self, config_file, output_file):

        """
        利用openSmile工具特征提取
        :param config_file: 配置文件
        :param output_file: 输出特征.csv文件（-O命令，默认ARFF格式），修改“-O”命令，输出openSMILE所支持的文件格式
        :return: None
        """

        cmd = "opensmile/build/progsrc/smilextract/SMILExtract -C %s -I %s -O %s" % (config_file, self.input_file, output_file)
        os.system(cmd)
        #subprocess.run(cmd,shell=True)
    
    def get_IS09(self,output_file):

        """
        提取IS09_emotion特征集中的384维特征，详见InterSpeech挑战赛论文集（The INTERSPEECH 2009 Emotion Challenge）：
        https://www.isca-speech.org/archive/archive_papers/interspeech_2009/papers/i09_0312.pdf
        :param output_file: 输出特征.csv文件（-O命令，默认ARFF格式），修改“-O”命令，输出openSMILE所支持的文件格式
        :return: 384维特征
        """
        self.feature_extraction(self.IS09_emotion, output_file)
        features = self.feature_file_reader(output_file)
        
        return features

    @staticmethod
    def feature_file_reader(feature_f):

        """
        读取生成的ARFF格式csv特征文件中特征值
        :param feature_f: ARFF格式csv特征文件
        :return: 特征
        """

        with open(feature_f) as f:

            last_line = f.readlines()[-1]  # ARFF格式csv文件最后一行包含特征数据

        features = last_line.split(",")

        features = np.array(features[1:-1], dtype="float64")  # 第2到倒数第二个为特征数据
        id_ = feature_f.split('/')[-1][:-4]
        loudness = features[19:38]
        loudness_de = features[513:532]
        pitch = features[456:475]
        pitch_de = features[950:969]
        loudness_var = features[418:437]
        loudness_var_de = features[912:931]
        verbosity = features[437:456]
        verbosity_de = features[931:950]
        features_needed = [id_,loudness,loudness_de,pitch,pitch_de,loudness_var,loudness_var_de,verbosity,verbosity_de]
        f = [y for x in features_needed for y in x]

        return f