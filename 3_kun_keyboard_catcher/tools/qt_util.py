#coding:utf-8
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import glob
import json
import os
from pathlib import PurePath
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
import pygame

import monitor

# 得到当前执行文件同级目录的其他文件绝对路径
def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)


class MainWidgets(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWidgets, self).__init__(parent)

        with open(resource_path('config.json')) as f:
            self.config = json.load(f)

        self.pos_first = self.pos()

        self.lab_bubble = QtWidgets.QLabel(self)
        self.lab_content = QtWidgets.QLabel(self)
        self.lab_content.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lab = QtWidgets.QLabel(self)

        self.font_big = QtGui.QFont()
        self.font_big.setFamily("微软雅黑")
        self.font_big.setPixelSize(35)
        self.font_big.setBold(True)

        self.font_small = QtGui.QFont()
        self.font_small.setFamily("微软雅黑")
        self.font_small.setPixelSize(25)
        self.font_small.setBold(True)

        # 定时器，用于长时间不输入清空输入状态和闭嘴
        # 以及清空输入历史
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reset_char)
        # 2秒定时清除文字
        self.timer.start(2000)

        # 历史输入
        # self.history_input = "#####"
        self.history_input = deque(maxlen=20)
        self.close_key = "nmyjj"

        # 按键-音效映射
        self.ch2audio = {}

        # 是否打开声音
        self.sound_flag = True
        # 初始化图片和音频
        self.init_resources()
        # 初始化监视器
        self.init_monitor()
        # 初始化窗口
        self.windowinit()
        # 初始化右下角角标
        self.icon_quit()
        # 创建线程池
        self.init_thread_pool()
        # 初始化pygame
        pygame.mixer.init()

    def init_resources(self):
        self.img_close_mouth = QtGui.QPixmap(resource_path(os.path.join("imgs", "cai1.png")))
        self.img_open_mouth = QtGui.QPixmap(resource_path(os.path.join("imgs", "cai2.png")))
        # 字母与音频对应关系
        self.init_ch2audio()
        self.hot_keys_func_map = {
            # "<ctrl>+j": lambda: self.play_audio(self.ch2audio["jntm"]),
            # "<ctrl>+j": self.play_ngm
        }
        # 如果对应位置有图片资源则使用其代替闭嘴、张嘴图; 如果有对应音频则替换键盘按键
        # 图片命名：
        #   0.png：闭嘴；1.png：张嘴
        # 音频命名：
        #   a.mp3: 键盘a和A摁下发出的声音；b.mp3: 键盘b和B摁下发出的声音
        #   c_a.mp3: 键盘ctrl+a快捷键发出的声音；c_b.mp3: 键盘ctrl+b快捷键发出的声音
    def init_ch2audio(self):
        if self.config['init_ch2audio_from_files']:
            self.init_ch2audio_from_files()
        if self.config['init_ch2audio_from_config']:
            self.init_ch2audio_from_config()

    def init_ch2audio_from_files(self):
        audio_files = resource_path(os.path.join('audios', '*.mp3'))
        for audio_file in glob.glob(audio_files):
            file_stem = PurePath(audio_file).stem
            self.ch2audio[file_stem.upper()] = audio_file

    def init_ch2audio_from_config(self):
        for key, audio_path_rel in self.config['init_ch2audio_config'].items():
            self.ch2audio[key.upper()] = resource_path(os.path.join('audios', audio_path_rel))

    def init_thread_pool(self, max_workers=None):
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    # 版本提示
    def version_content(self):
        QtWidgets.QMessageBox.information(self, "坤音键盘v1.3", "抖音/B站：走神的阿圆 QQ群:766402914",
                                QtWidgets.QMessageBox.StandardButton.Yes)

    # 弹出提示
    def open_qq_group(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://jq.qq.com/?_wv=1027&k=A1DK3FhW'))

    # 松开键盘时
    def on_release(self, key):
        # 闭嘴
        self.lab.setPixmap(self.img_close_mouth)
        self.lab.adjustSize()

    # 摁下键盘时
    def on_press(self, key):
        try:
            ch = key.char
        except AttributeError:
            ch = key.name
        self.set_char(ch)


    def init_monitor(self):
        self.monitor = monitor.KeyBoardLister(on_press_func=self.on_press, on_release_func=self.on_release, hot_keys_func_map=self.hot_keys_func_map)

    def windowinit(self):
        # 初始窗口设置大一点以免放入的图片显示不全
        self.pet_width = 200
        self.pet_height = 200
        # 获取桌面桌面大小决定宠物的初始位置为右上角
        desktop = QtWidgets.QApplication.desktop()
        self.x = desktop.width()-self.pet_width
        self.y = 100
        #self.setGeometry(self.x, self.y, self.pet_width, self.pet_height)
        self.setWindowTitle('坤音键盘-by 走神的阿圆')

        # 显示字母
        self.lab_content.setFont(self.font_big)
        self.lab_content.setStyleSheet("color:black;")
        self.lab_content.move(38, 28)

        # 气泡框
        self.lab_bubble.move(0, 0)
        self.lab_bubble.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "bubble.png"))))

        # 坤人
        self.lab.move(50, 50)
        self.lab.setPixmap(self.img_close_mouth)
        self.lab.adjustSize()


        # 设置窗口为 无边框 | 保持顶部显示 | 任务栏不显示图标
        self.setWindowFlags(
                QtCore.Qt.WindowType.FramelessWindowHint|QtCore.Qt.WindowType.WindowStaysOnTopHint|QtCore.Qt.WindowType.WindowStaysOnTopHint|QtCore.Qt.WindowType.Tool
                )
        # # 设置窗口透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

    # 使用pygame播放
    def play_sound(self, path):
       pygame.mixer.Sound(path).play()

    # 开线程放音乐，避免阻断主流程，实现可以同时放多个radio
    def play_audio(self, path):
        # 1 不使用线程池
        # t = threading.Thread(target=self.test, args=(path,))
        # t.start()
        # 2 使用线程池
        if self.sound_flag:
            self.pool.submit(self.play_sound, path)

    def set_char(self, ch):
        if ch is None:
            return
        ch = ch.upper()
        if ch in self.ch2audio:
            self.play_audio(self.ch2audio[ch])

        # 设置字母
        if len(ch) == 1:
            font = self.font_big
            pos = (40, 28)
            self.history_input.append(ch)
            for key_seq in self.ch2audio.keys():
                if len(key_seq) == 1:
                    continue
                if ''.join(self.history_input).endswith(key_seq):
                    self.play_audio(self.ch2audio[key_seq])
                    self.history_input.clear()
                    break
                # raise RuntimeError("你这个假ikun！")
        else:
            font = self.font_small
            pos = (28, 28)

        # 显示字母
        self.lab_content.setFont(font)
        self.lab_content.move(*pos)
        self.lab_content.setText(ch)
        self.lab_content.adjustSize()

        # 张嘴
        self.lab.setPixmap(self.img_open_mouth)
        self.lab.adjustSize()


    # 长时间没有触发则要回归到最初状态
    def reset_char(self):
        # 清除文字
        self.lab_content.setText("")
        self.lab_content.adjustSize()
        # 闭嘴
        self.lab.setPixmap(self.img_close_mouth)
        self.lab.adjustSize()

    # 此函数和mouseMoveEvent配合可以完成拖动功能
    # 鼠标左键按下的时候获取当前位置
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.MouseButton.LeftButton:
            self.pos_first = QMouseEvent.globalPos() - self.pos()
            QMouseEvent.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))

    # 设置可以拖动
    def mouseMoveEvent(self, QMouseEvent):
        self.move(QMouseEvent.globalPos() - self.pos_first)
        QMouseEvent.accept()

    def icon_quit(self):
        # 托盘
        mini_icon = QtWidgets.QSystemTrayIcon(self)
        mini_icon.setIcon(QtGui.QIcon(resource_path(os.path.join("imgs", "cai2.png"))))
        mini_icon.setToolTip("坤音键盘-by 走神的阿圆")
        # 为托盘增加一个菜单选项
        tpMenu = QtWidgets.QMenu(self)
        # 为菜单指定一个选项

        version_menu =  QtWidgets.QAction('作者', self, triggered=self.version_content)
        tpMenu.addAction(version_menu)
        quit_menu_qq = QtWidgets.QAction('获取更多', self, triggered=self.open_qq_group)
        tpMenu.addAction(quit_menu_qq)
        self.sound_key_menu = QtWidgets.QAction('关闭声音', self, triggered=self.change_sound)
        tpMenu.addAction(self.sound_key_menu)
        quit_menu = QtWidgets.QAction('退出', self, triggered=self.quit)
        tpMenu.addAction(quit_menu)

        mini_icon.setContextMenu(tpMenu)
        mini_icon.show()

    def change_sound(self):
        if self.sound_key_menu.text() == "关闭声音":
            self.sound_flag = False
            self.sound_key_menu.setText("打开声音")
        elif self.sound_key_menu.text() == "打开声音":
            self.sound_flag = True
            self.sound_key_menu.setText("关闭声音")

    def quit(self):
        self.close()
        sys.exit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    pet = MainWidgets()
    sys.exit(app.exec())
