#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2021/2/20 18:19
# @Author  : xiaorun
# @Site    :
# @File    : yoloDetect.py
# @Software: PyCharm
import sys
import threading
from threading import Thread
import time
import os
import cv2
# from yolo import YOLO5
import json,jsonify
import requests
import flask
from flask import request
headers = {'Content-Type': 'application/json'}
url_addr="http://123.206.106.55:8065/api/video/getPersonNum/"

# 创建一个服务，把当前这个python文件当做一个服务
server = flask.Flask(__name__)

server.debug = True

def gen_detector(url_video):
    yolo = YOLO5()
    opt = parseData()
    yolo.set_config(opt.weights, opt.device, opt.img_size, opt.conf_thres, opt.iou_thres, True)
    yolo.load_model()
    camera = cv2.VideoCapture(url_video)
    # 读取视频的fps,  大小
    fps = camera.get(cv2.CAP_PROP_FPS)
    size = (camera.get(cv2.CAP_PROP_FRAME_WIDTH), camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print("fps: {}\nsize: {}".format(fps, size))

    # 读取视频时长（帧总数）
    total = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
    print("[INFO] {} total frames in video".format(total))
    ret, frame = camera.read()
    if ret==False:
        video_parameter = {"accessKey": "1C7C48F44A3940EBBAQXTC736BF6530342",
                           "code": "0000",
                        "personNum": "video problem.."}
        response = requests.post(url=url_addr, headers=headers, data=json.dumps(video_parameter))
        print(response.json())

    max_person=0
    while total>0:
        total=total-1
        ret,frame=camera.read()
        if ret == True:
            objs = yolo.obj_detect(frame)
            if max_person<=len(objs):
                max_person=len(objs)
            for obj in objs:
                cls = obj["class"]
                cor = obj["color"]
                conf = '%.2f' % obj["confidence"]
                label = cls + " "
                x, y, w, h = obj["x"], obj["y"], obj["w"], obj["h"]
                cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), tuple(cor))
                cv2.putText(frame, label, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, thickness=2)
            person = "there are {} person ".format(len(objs))
            cv2.putText(frame, person, (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), thickness=3)
            video_parameter = {"accessKey": "1C7C48F44A3940EBBAQXTC736BF6530342",
                               "code": "0000",
                               "personNum": str(max_person)}
            if total==0:
                response = requests.post(url=url_addr, headers=headers, data=json.dumps(video_parameter))
                print(response.json())
            cv2.imshow("test",frame)
            if cv2.waitKey(1)==ord("q"):
                break

@server.route('/video', methods=['post'])
def get_video():
    if not request.data:  # 检测是否有数据
        return ('fail..')
    video_name= request.data.decode('utf-8')
    # 获取到POST过来的数据，因为我这里传过来的数据需要转换一下编码。根据晶具体情况而定
    video_json = json.loads(video_name)
    print(video_json)
    accessKey=video_json["accessKey"]

    if accessKey=="1C7C48F44A3940EBBAQXTC736BF6530342":

        code=video_json["code"]
        url_video=video_json["url"]
        print(url_video)
        gen_detector(url_video)
        # 把区获取到的数据转为JSON格式。
        data_return={"code":200,"data":url_video,"message":"请求成功","sucsess":"true"}
        return json.dumps(data_return)
    else:
        pass
    # 返回JSON数据。

if __name__ == '__main__':
    server.run(host='192.168.1.250', port=8888)
