import sys

if sys.version_info[0] < 3 and sys.version_info[1] < 2:
	raise Exception("Must be using >= Python 3.2")

from os import listdir, path

if not path.isfile('face_alignment/detection/sfd/s3fd.pth'):
	raise FileNotFoundError('Save the s3fd model to face_detection/detection/sfd/s3fd.pth \
							before running this script!')

import multiprocessing as mp
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
import argparse, os, cv2, traceback, subprocess
from glob import glob
import face_alignment


fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, flip_input=False, face_detector='blazeface', device='cuda:{}'.format(0))

template = 'ffmpeg -loglevel panic -y -i {} -strict -2 {}'
# template2 = 'ffmpeg -hide_banner -loglevel panic -threads 1 -y -i {} -async 1 -ac 1 -vn -acodec pcm_s16le -ar 16000 {}'

def process_video_file():
    video_stream = cv2.VideoCapture(0)
    frames = []
    while 1:
        still_reading, frame = video_stream.read()
        preds = fa.get_landmarks(frame,return_bboxes=True)
        if preds != (None, None, None):
            cords=[]
            print(preds)
            for i in enumerate(preds[2][0]):
                _ , x = i
                cords.append(x)
            x1, y1, x2, y2, _= cords
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('p'):
                break
        

    
if __name__ == '__main__':
	process_video_file()