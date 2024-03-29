import sys
import cv2
import numpy as np
import math
import os
import time
import random

from PyQt5 import QtWidgets, QtCore, QtGui
import Ui_rotate_img
import moviepy.editor as mov # python多媒体编辑

# 以图片中间为中轴旋转一度
# 假设长度为L，高度为H，初始状态投影到背后坐标为 左上(0,0), 左下(0,H), 右上(L, 0), 右下(L,H)，中间轴上(L/2, 0)，中间轴下(L/2,H)
# 右边往前，左边往后，中间轴不动的方式旋转一度
# x坐标变化：则投影后的x坐标为左边为(L/2 - L/2*Cos(1°*2))，右边(L/2 + L/2*Cos(1°))，
# y坐标变化：假设y不变，那么总坐标为 左上(L/2 - L/2*Cos(1°), 0)，左下(L/2 - L/2*Cos(1°), H)，右上(L/2 + L/2*Cos(1°), 0)，右下(L/2 + L/2*Cos(1°)，H)
def rotate(img, degree=1, reverse=False):
    width = img.shape[0]
    length = img.shape[1]
    radius = degree*math.pi/180
    pos1 = np.float32([[0, 0], [0, width], [length, 0], [length, width]])
    pos2 = np.float32([[length/2-length/2*math.cos(radius), 0], [length/2-length/2*math.cos(radius), width], [length/2+length/2*math.cos(radius), 0], [length/2+length/2*math.cos(radius), width]])
    pos2 = np.float32([[length/2-length/2*math.cos(radius), width/5*math.sin(radius)], [length/2-length/2*math.cos(radius), width- width/5*math.sin(radius)], [length/2+length/2*math.cos(radius), -width/5*math.sin(radius)], [length/2+length/2*math.cos(radius), width+width/5*math.sin(radius)]])
    M = cv2.getPerspectiveTransform(pos1, pos2)
    result = cv2.warpPerspective(img, M, (length, width))
    return result

def next_location(top_left_point, velocity, background_img_shape, img_shape):
    # 按照速度和位置计算下一个位置是否超出背景图，如果x轴超出则x方向速度取反，y轴亦然
    next_top_left_point_tmp = [top_left_point[0]+velocity[0], top_left_point[1]+velocity[1]]
    # 图片最左边出现在背景图更左，说明碰到了左边的边界；图片最右边出现在背景图更右，说明碰到了右边的边界。x轴方向速度取反
    if next_top_left_point_tmp[0] < 0 or next_top_left_point_tmp[0]+img_shape[0] > background_img_shape[0]:
        velocity[0] = -velocity[0]
    # 图片最上面出现在背景图更上，说明碰到了上边的边界；图片最下边出现在背景图更下，说明碰到了下边的边界。y轴方向速度取反
    if next_top_left_point_tmp[1] < 0 or next_top_left_point_tmp[1]+img_shape[1] > background_img_shape[1]:
        velocity[1] = -velocity[1]
    # 返回实际位置和速度
    return [top_left_point[0]+velocity[0], top_left_point[1]+velocity[1]], velocity

# 根据一张图生成img_nums张图，均分360°，即从正面旋转到反面(180°)，再转到正面(360°)
def generate_rotate_move_imgs(input_img_path, img_nums_all, img_nums=60, velocity=[1,1], top_left_point=[0,0], use_file=False, output_dir=None):
    # 默认在输入图片所在文件夹新建输出文件夹
    timestamp = int(time.time())
    if not output_dir:
        input_dir = os.path.dirname(os.path.abspath(input_img_path))
        output_dir = os.path.join(input_dir, "output_{}".format(timestamp))
    if use_file and not os.path.exists(output_dir):
        os.mkdir(output_dir)

    result_imgs = []
    # 生成img_nums张图并保存
    img = cv2.imdecode(np.fromfile(input_img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    # 获取图片的原尺寸，用于生成一张黑色背景图
    weight = img.shape[0]
    height = img.shape[1]
    background_img = np.zeros((weight, height, img.shape[2]), np.uint8)
    background_img.fill(0)
    # shape的格式 (宽，高，通道数)，而resize的格式是先高再宽，这要注意
    # (TODO:后续改成界面可配置)先将图片缩放之前的1/3，透视变换后再通过扩充白色边缘变为原图尺寸
    img = cv2.resize(img, (img.shape[1]//3, img.shape[0]//3))
    for i in range(img_nums_all):
        degree = int(360/img_nums) * i % 360
        if int(degree) == 90 or int(degree) == 270:
            continue
        result = rotate(img, degree=degree)
        print("生成第{}张图成功，degree: {}°".format(i+1, degree))
        # 扩充边缘为黑色恢复原图尺寸
        top_border_size = (result.shape[1]*3-result.shape[1])//2
        left_border_size = (result.shape[0]*3-result.shape[0])//2
        # 填充边缘黑色的方式来生成图片
        # result = cv2.copyMakeBorder(result, top_border_size, top_border_size, left_border_size, left_border_size, cv2.BORDER_CONSTANT, value=[0]*result.shape[2])
        # 图片嵌入的方式生成图片
        background_img_tmp = background_img.copy()
        # 根据速度和当前位置，背景图片大小和素材图片大小获取下一个位置和速度
        top_left_point, velocity = next_location(top_left_point, velocity, background_img_tmp.shape, result.shape)
        background_img_tmp[top_left_point[0]:top_left_point[0]+result.shape[0], top_left_point[1]:top_left_point[1]+result.shape[1]] = result
        # cv2.imshow("img", background_img_tmp)
        # cv2.waitKey(0)
        # raise RuntimeError("88888888888888888888")
        # print("background_img_tmp = ", id(background_img_tmp), " result = ", result)
        result_imgs.append(background_img_tmp)
        if use_file:
            cv2.imwrite(os.path.join(output_dir, "output_{}.png".format(degree)), background_img_tmp)

    # return result_imgs, output_dir, top_left_point, velocity
    return result_imgs, output_dir

# 根据一张图生成img_nums张图，均分360°，即从正面旋转到反面(180°)，再转到正面(360°)
def generate_rotate_imgs(input_img_path, img_nums=60, use_file=False, output_dir=None):
    # 默认在输入图片所在文件夹新建输出文件夹
    timestamp = int(time.time())
    if not output_dir:
        input_dir = os.path.dirname(os.path.abspath(input_img_path))
        output_dir = os.path.join(input_dir, "output_{}".format(timestamp))
    if use_file and not os.path.exists(output_dir):
        os.mkdir(output_dir)

    result_imgs = []
    # 生成img_nums张图并保存
    img = cv2.imdecode(np.fromfile(input_img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    # (TODO:后续改成界面可配置)先将图片缩放之前的1/3，透视变换后再通过扩充白色边缘变为原图尺寸
    img = cv2.resize(img, (img.shape[0]//3, img.shape[1]//3))
    for i in range(img_nums):
        degree = 360/img_nums*i
        if int(degree) == 90 or int(degree) == 270:
            continue
        result = rotate(img, degree=degree)
        print("生成第{}张图成功，degree: {}°".format(i+1, degree))
        # 扩充边缘为白色恢复原图尺寸
        top_border_size = (result.shape[1]*3-result.shape[1])//2
        left_border_size = (result.shape[0]*3-result.shape[0])//2
        result = cv2.copyMakeBorder(result, top_border_size, top_border_size, left_border_size, left_border_size, cv2.BORDER_CONSTANT, value=[0]*result.shape[2])
        result_imgs.append(result)
        if use_file:
            cv2.imwrite(os.path.join(output_dir, "output_{}.png".format(degree)), result)

    return result_imgs, output_dir

# 将图片生成视频
def img2Video(result_imgs, input_path, oneLoopSeconds, totalSeconds, repeat=True, output_path=None):
    timestamp = int(time.time())
    # 设置写入格式为mp4
    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'b')
    # 一圈需要len(result_imgs)张图，而一圈是oneLoopSeconds秒，因此帧速率fps=len(result_imgs)//oneLoopSeconds，这里必须保证fps是正值
    if repeat:
        fps = len(result_imgs)//oneLoopSeconds
    else:
        fps = len(result_imgs)//totalSeconds
    print("fps = ", fps, " nums = ", len(result_imgs), " oneLoopSeconds = ", oneLoopSeconds, " totalSeconds = ", totalSeconds)
    # 初始化媒体写入对象
    if not output_path:
        output_path = os.path.join(os.path.dirname(input_path), "output_{}.mp4".format(timestamp))
    img_size = (result_imgs[0].shape[1], result_imgs[0].shape[0])
    media_writer = cv2.VideoWriter(output_path, fourcc, fps, img_size)
    # for j in range(len(result_imgs)):
    #     np.where(result_imgs[j], )
    #     print("处理第{}张图片去透明化".format(j))
    #     # 如果是四通道的png图片，将透明部分转为黑色
    #     if (result_imgs[j].shape[2]) == 4:
    #         for yh in range(result_imgs[j].shape[1]):
    #             for xw in range(result_imgs[j].shape[0]):
    #                 if result_imgs[j][xw, yh][3] == 0:
    #                     result_imgs[j][xw, yh] = [0, 0, 0, 255]
    # 每张图片加入视频中，两层循环
    # 外层循环：每次转一圈
    # 内部循环：每圈图片写入
    # 移动鸡块模式下，不会出现重复帧
    if not repeat:
        totalSeconds = oneLoopSeconds
    for i in range(totalSeconds//oneLoopSeconds):
        for j in range(len(result_imgs)):
            media_writer.write(result_imgs[j])
    media_writer.release()
    print("无声视频产出完成！等待添加背景音乐")
    return output_path

def set_video_music(video_mute_path, input_radio_path):
    print("开始添加背景音乐, 视频：{}, 音频：{}".format(video_mute_path, input_radio_path))
    timestamp = int(time.time())
    # 初始化视频文件对象
    video_clip = mov.VideoFileClip(video_mute_path)
    # 初始化背景音乐
    audio_clip = mov.AudioFileClip(input_radio_path)
    # 设置背景音乐循环，时间与视频时间一致
    audio = mov.afx.audio_loop(audio_clip, duration=video_clip.duration)
    # 视频添加背景音乐
    final_video = video_clip.set_audio(audio)
    # 保存，删掉无声视频，保存新视频
    final_video_path = os.path.join(os.path.dirname(input_radio_path), "output_rotate_{}.mp4".format(timestamp))
    final_video.write_videofile(final_video_path)
    # final_video.ipython_display()
    return final_video_path

# 将random_img_dir中的图片随机嵌入到imgs中
def randomImgInsert(imgs, random_img_dir):
    if not random_img_dir:
        return imgs

    contents = os.listdir(random_img_dir)
    files = filter(lambda f: os.path.isfile(os.path.join(random_img_dir, f)), contents)
    for file in files:
        file = os.path.join(random_img_dir, file)
        # 生成img_nums张图并保存
        img = cv2.imdecode(np.fromfile(file, dtype=np.uint8), cv2.IMREAD_UNCHANGED)

        random_img_index = random.randint(0, len(imgs)-1)
            # 获取图片的原尺寸，用于生成一张黑色背景图
        weight = imgs[random_img_index].shape[0]
        height = imgs[random_img_index].shape[1]
        # background_img = np.zeros((height, weight, img.shape[2]), np.uint8)
        # background_img.fill(0)
        img = cv2.resize(img, (height, weight))
        # print("img.shape = ", img.shape, " old img shape = ", imgs[random_img_index].shape)
        imgs[random_img_index][0:weight, 0:height] = img[0:weight, 0:height]
    return imgs

class RotateImgTool(Ui_rotate_img.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super(RotateImgTool, self).__init__(parent)
        self.setupUi(self)

        # 路径不能编辑只能复制
        self.lineEdit.setReadOnly(True)
        self.lineEdit_2.setReadOnly(True)
        # 图片张数限制整数，默认30张
        self.lineEdit_3.setValidator(QtGui.QIntValidator(1, 360))
        self.lineEdit_3.setText(str(30))
        self.img_nums = 30
        # 一圈旋转时间限制整数，默认10秒
        self.lineEdit_4.setValidator(QtGui.QIntValidator(1, 3600))
        self.lineEdit_4.setText(str(10))
        self.oneLoopSeconds = 10
        # 总旋转时间限制整数，默认60秒
        self.lineEdit_5.setValidator(QtGui.QIntValidator(1, 3600))
        self.lineEdit_5.setText(str(60))
        self.totalSeconds = 60

        # 默认使用内存，不生成图片文件
        self.use_file = False
        # 存储映射后的图片
        self.result_imgs = []
        self.checkBox_2.setChecked(False)
        self.output_dir = None

        # 默认不移动鸡块位置
        self.checkBox.setChecked(False)

        # 读取图片
        # 原始图片文件
        self.input_img_file = ""
        self.pushButton.clicked.connect(self.chooseImgFile)
        # 读取音乐
        self.input_audio_file = ""
        self.pushButton_2.clicked.connect(self.chooseAudioFile)
        # 添加随机图片文件夹
        self.input_random_img_dir = ""
        self.pushButton_4.clicked.connect(self.chooseRandomImgDir)
        # 生成视频
        self.pushButton_3.clicked.connect(self.generateRotateVideo)

        self.checkBox.toggled.connect(self.canSelectVelocity)

        # 鸡块的初始位置在左上角
        self.top_left_point = [0, 0]
        self.lineEdit_7.setDisabled(True)
        
        # 鸡块的初始速度，数组表示矢量在x和y轴的分解
        self.velocity = [5, 5]

    # 选择速度
    def canSelectVelocity(self):
        if self.checkBox.isChecked():
            self.lineEdit_7.setEnabled(True)
            self.lineEdit_7.setText(str(5))
        else:
            self.lineEdit_7.setDisabled(True)
            self.lineEdit_7.setText("")

    # 读取随机图片文件夹，将随机图片用于后续随机插入到视频钟
    def chooseRandomImgDir(self):
        # 创建文件夹对话框
        dir = QtWidgets.QFileDialog.getExistingDirectory(None, "选择文件夹路径", os.getcwd())
        self.lineEdit_6.setText(dir)
        self.input_random_img_dir = dir

    # 读取图片并展示
    def chooseImgFile(self):
        # 创建文件对话框
        dir = QtWidgets.QFileDialog()
        # 设置单选
        dir.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        # 设置默认打开路径
        dir.setDirectory(".")
        # 设置能打开的文件类型
        dir.setNameFilter("视频文件(*.jpg *.png *.jpeg)")
        # 判断是否选择了文件
        if dir.exec():
            self.input_img_file = dir.selectedFiles()[0]
            self.lineEdit.setText(self.input_img_file)
            pixmap = QtGui.QPixmap(self.input_img_file)
            self.label.setPixmap(self.scalePixmapInLabel(self.label, pixmap))
            # self.label.setScaledContents(True)
            self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

    # 读取音乐作为循环的背景音乐
    def chooseAudioFile(self):
        # 创建文件对话框
        dir = QtWidgets.QFileDialog()
        # 设置单选
        dir.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        # 设置默认打开路径
        dir.setDirectory(".")
        # 设置能打开的文件类型
        dir.setNameFilter("音频文件(*.mp3)")
        # 判断是否选择了文件
        if dir.exec():
            self.input_audio_file = dir.selectedFiles()[0]
            self.lineEdit_2.setText(self.input_audio_file)

    # 弹出是否确认对话框
    def make_sure(self):
        # 获取单个文件大小
        file_size = os.path.getsize(self.input_img_file)
        # 一共使用的文件数量
        total_size = int(self.lineEdit_5.text())//int(self.lineEdit_4.text())*int(self.lineEdit_3.text())*file_size/1024/1024
        reply = QtWidgets.QMessageBox.question(self, '提示', '需要占用硬盘大小约{}mb(不代表最终文件)，确认生成？'.format(int(total_size)),QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

    # 生成旋转物体的视频
    def generateRotateVideo(self):
        self.use_file = self.checkBox.isChecked()
        print("参数 是否保存文件:{}, 生成图像数量: {}, 单圈旋转时间: {}, 视频总时长: {}".format(self.checkBox_2.isChecked(), self.lineEdit_3.text(), self.lineEdit_4.text(), self.lineEdit_5.text()))
        if int(self.lineEdit_3.text()) < int(self.lineEdit_4.text()):
            reply = QtWidgets.QMessageBox.warning(self, '提示', '图像数量必须大于旋转一圈时间！',QtWidgets.QMessageBox.Yes)
            return
        if not self.make_sure():
            print("已经取消视频生成！")
            return
        print("开始生成视频")
        # 获取旋转后的图片
        self.img_nums = int(self.lineEdit_3.text())
        # 移动鸡块
        if self.checkBox.isChecked():
            self.velocity = [int(self.lineEdit_7.text()), int(self.lineEdit_7.text())]
            # 图片总数 = 单圈数量*（总时长/单圈时长）
            img_nums_all = self.img_nums*int(self.lineEdit_5.text())//int(self.lineEdit_4.text())
            self.result_imgs, self.output_dir = generate_rotate_move_imgs(
                input_img_path=self.input_img_file,
                img_nums_all=img_nums_all,
                img_nums=self.img_nums,
                velocity=self.velocity,
                top_left_point=self.top_left_point,
                use_file=self.use_file
                )
            self.result_imgs = randomImgInsert(self.result_imgs, self.input_random_img_dir)
            # 图片转成视频，要根据旋转时长确定帧速率
            self.oneLoopSeconds = int(self.lineEdit_4.text())
            self.totalSeconds = int(self.lineEdit_5.text())
            video_mute_path = img2Video(
                result_imgs=self.result_imgs,
                input_path=self.input_img_file,
                oneLoopSeconds=self.oneLoopSeconds,
                totalSeconds=self.totalSeconds,
                repeat=False
                )
        # 普通鸡块
        else:
            self.result_imgs, self.output_dir = generate_rotate_imgs(
                input_img_path=self.input_img_file,
                img_nums=self.img_nums,
                use_file=self.use_file
                )
            # 图片转成视频，要根据旋转时长确定帧速率
            self.oneLoopSeconds = int(self.lineEdit_4.text())
            self.totalSeconds = int(self.lineEdit_5.text())
            video_mute_path = img2Video(
                result_imgs=self.result_imgs,
                input_path=self.input_img_file,
                oneLoopSeconds=self.oneLoopSeconds,
                totalSeconds=self.totalSeconds,
                repeat=True
                )

        
        # 将无声视频添加声音
        if self.input_audio_file:
            final_video_path = set_video_music(video_mute_path, self.input_audio_file)
            # 删除无声视频
            os.remove(video_mute_path)
            video_mute_path = final_video_path
        QtWidgets.QMessageBox.information(None, "提示", "视频生成成功，路径{}".format(video_mute_path), QtWidgets.QMessageBox.StandardButton.Ok)
        os.startfile(os.path.dirname(video_mute_path)) # 只打开文件夹不选中文件


    # 将过大的pixmap等比例缩放至匹配所在label
    def scalePixmapInLabel(self, label:QtWidgets.QLabel, pixmap:QtGui.QPixmap):
        label_width = label.width()
        label_height = label.height()
        pixmap_width = pixmap.width()
        pixmap_height = pixmap.height()
        if label_width >= pixmap_width and label_height >= pixmap_height:
            return pixmap
        # label宽度相比长度更长，因此将图片长度保持和label相同，宽度等比例缩小
        if label_width/pixmap_width > label_height/pixmap_height:
            return pixmap.scaled(label_height*pixmap_width//pixmap_height, label_height)
        else:
            return pixmap.scaled(label_width, label_width*pixmap_height//pixmap_width)

if __name__ == "__main__":
    print("审核快乐器v1.0加载中，请稍后...")
    app = QtWidgets.QApplication(sys.argv)
    rotate_img_tool = RotateImgTool()
    rotate_img_tool.show()
    print("审核快乐器v1.0加载成功！")
    sys.exit(app.exec())