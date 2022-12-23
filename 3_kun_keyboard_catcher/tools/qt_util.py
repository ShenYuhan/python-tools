#coding:utf-8
import functools
import sys
import os
from concurrent.futures import ThreadPoolExecutor

from PyQt5 import QtGui, QtWidgets, QtCore
from pynput.keyboard import Key
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
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reset_char)
        # 3秒定时清除文字
        self.timer.start(3000)

        # 历史输入
        self.history_input = "#####"
        self.close_key = "nmyjj"

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
        self.ch2audio = {
            # 'e': resource_path(os.path.join("audios", "e.mp3")),
            # 'h': resource_path(os.path.join("audios", "h.mp3")),
            # '114514': resource_path(os.path.join("audios", "114514.mp3")),
            '1': resource_path(os.path.join("audios", "1.mp3")),
            'b': resource_path(os.path.join("audios", "b.mp3")),
            'c': resource_path(os.path.join("audios", "c.mp3")),
            'k': resource_path(os.path.join("audios", "k.mp3")),
            'l': resource_path(os.path.join("audios", "l.mp3")),
            'r': resource_path(os.path.join("audios", "r.mp3")),
            'j': resource_path(os.path.join("audios", "j.mp3")),
            'J': resource_path(os.path.join("audios", "j.mp3")),
            'n': resource_path(os.path.join("audios", "n.mp3")),
            'N': resource_path(os.path.join("audios", "n.mp3")),
            't': resource_path(os.path.join("audios", "t.mp3")),
            'T': resource_path(os.path.join("audios", "t.mp3")),
            'm': resource_path(os.path.join("audios", "m.mp3")),
            'M': resource_path(os.path.join("audios", "m.mp3")),
            'jntm': resource_path(os.path.join("audios", "ngm.mp3")),
            'nmyjj': resource_path(os.path.join("audios", "ngm.mp3")),
        }
        self.hot_keys_func_map = {
            # "<ctrl>+j": functools.partial(self.play_audio, path=self.ch2audio["jntm"])
            # "<ctrl>+j": self.play_ngm
        }
        # 如果对应位置有图片资源则使用其代替闭嘴、张嘴图; 如果有对应音频则替换键盘按键
        # 图片命名：
        #   0.png：闭嘴；1.png：张嘴
        # 音频命名：
        #   a.mp3: 键盘a和A摁下发出的声音；b.mp3: 键盘b和B摁下发出的声音
        #   c_a.mp3: 键盘ctrl+a快捷键发出的声音；c_b.mp3: 键盘ctrl+b快捷键发出的声音
        conf_dirs = ["D:/ikun/", "D:/Program Files (x86)/ikun/", "D:/Program Files/ikun/", "C:/Program Files/ikun/", "C:/Program Files (x86)/ikun/"]
        for conf_dir in conf_dirs:
            if os.path.exists(conf_dir) and os.path.isdir(conf_dir):
                if os.path.exists(os.path.join(conf_dir, "0.png")):
                    self.img_close_mouth = QtGui.QPixmap(os.path.join(conf_dir, "0.png"))
                if os.path.exists(os.path.join(conf_dir, "1.png")):
                    self.img_open_mouth = QtGui.QPixmap(os.path.join(conf_dir, "1.png"))
                for root, _, files in os.walk(conf_dir):
                    for path in files:
                        if os.path.splitext(path)[-1] == ".mp3":
                            self.ch2audio.update({os.path.splitext(path)[0]: os.path.join(root, path)})
                            if os.path.splitext(path)[0].startswith("c_"):
                                self.hot_keys_func_map.update({"<ctrl>+{}".format(str(os.path.splitext(path)[0]).split('_')[-1]): functools.partial(self.play_audio, path=self.ch2audio[os.path.splitext(path)[0]])})      

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
        self.setGeometry(self.x, self.y, self.pet_width, self.pet_height)
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
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint| QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.SplashScreen)
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
        if ch in self.ch2audio:
            self.play_audio(self.ch2audio[ch])

        # 设置字母
        if len(ch) == 1:
            # 显示字母
            self.lab_content.setFont(self.font_big)
            self.lab_content.move(40, 28)
            # 只有单字母才计入历史，模拟定长队列加新的第一位
            self.history_input = self.history_input[1:] + ch
            if self.history_input[len(self.history_input)-len(self.close_key):] == self.close_key:

                self.play_audio(self.ch2audio[self.close_key])
                # raise RuntimeError("你这个假ikun！")
        else:
            # 显示字母
            self.lab_content.setFont(self.font_small)
            self.lab_content.move(28, 28)
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
    sys.exit(app.exec_())