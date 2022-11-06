# encoding:utf-8

import requests
import os
import base64
import time

'''
人像分割
'''
def request_image_classify(filepath, now_timestamp):
    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_seg"
    # 二进制方式打开图片文件
    f = open(filepath, 'rb')
    img = base64.b64encode(f.read())
    
    output_dir = os.path.join(os.path.dirname(filepath), "image_classify_output_" + now_timestamp)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    params = {"image":img}
    access_token = '24.0f9e6b1f730cdc4497f93f8605f3a92e.2592000.1670289258.282335-28272275'
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers)
    if response:
        output_base64 = response.json()["foreground"]
        img_data = base64.b64decode(output_base64)
        with open(os.path.join(output_dir, os.path.basename(filepath)), "wb") as fp:
            fp.write(img_data)
            print(os.path.join(output_dir, os.path.basename(filepath)), " success")

if __name__ == "__main__":
    now_timestamp = str(int(time.time()))
    dirname = "D:/Program Files (x86)/pet_conf/output_1667720172/"
    for root, dirs, files in os.walk(dirname):
        if os.path.abspath(root) == os.path.abspath(dirname):
            for filename in files:
                request_image_classify(os.path.join(root, filename), now_timestamp)
    
