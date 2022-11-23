#coding:utf-8
import sys
import os
from PyQt5 import QtGui, QtWidgets, QtCore
import monitor
from pynput.keyboard import Key
import playsound
import threading
import urllib.request


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # print("1111")
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath('.')
    # print("base_path = ", base_path)
    return os.path.join(base_path, relative_path)


class MainWidgets(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MainWidgets, self).__init__(parent)

        self.pos_first = self.pos()

        self.lab_bubble = QtWidgets.QLabel(self)        
        self.lab_content = QtWidgets.QLabel(self)
        self.lab_content.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.lab = QtWidgets.QLabel(self)

        # 定时器，用于长时间不输入清空输入状态和闭嘴
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reset_char)
        self.timer.start(3000)

        # 字母与音频对应关系
        self.ch2audio = {
            # 'j': os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", "j.mp3"),
            'j': resource_path(os.path.join("audios", "j.mp3")),
            'n': resource_path(os.path.join("audios", "n.mp3")),
            't': resource_path(os.path.join("audios", "t.mp3")),
            'm': resource_path(os.path.join("audios", "m.mp3")),
            'J': resource_path(os.path.join("audios", "j.mp3")),
            'N': resource_path(os.path.join("audios", "n.mp3")),
            'T': resource_path(os.path.join("audios", "t.mp3")),
            'M': resource_path(os.path.join("audios", "m.mp3")),
            'jntm': resource_path(os.path.join("audios", "ngm.mp3"))
            # 'n': os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", "n.mp3"),
            # 't': os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", "t.mp3"),
            # 'm': os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", "m.mp3"),
            # 'J': os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", "j.mp3"),
            # 'N': os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", "n.mp3"),
            # 'T': os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", "t.mp3"),
            # 'M': os.path.join(os.path.dirname(os.path.abspath(__file__)), "audios", "m.mp3")
        }
        self.init_monitor()
        
        self.windowinit()
        self.icon_quit()

    def open_qq_group(self):
        QtWidgets.QMessageBox.information(self, "走神的阿圆", "抖音/B站：走神的阿圆 QQ群:766402914",
                            QtWidgets.QMessageBox.StandardButton.Yes)
        urllib.request.urlopen("https://jq.qq.com/?_wv=1027&k=A1DK3FhW")

    # 松开键盘时
    def on_release(self, key):
        # 闭嘴
        self.lab.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "cai1.png"))))
        # try:
            # print("alphanueric jkey {} pressed".format(key.char))
        # except AttributeError:
            # print("spcial key {0} pressed".format(key))

    # 摁下键盘时
    def on_press(self, key):
        # print("{0} released".format(key))
        if key == Key.esc:
            # esc停止监测
            return False
        try:
            ch = key.char
        except AttributeError:
            ch = key.name
        self.set_char(ch)

    def play_ngm(self):
        t = threading.Thread(target=self.play_radio, args=(self.ch2audio["jntm"],))
        t.start()

    def init_monitor(self):
        hot_keys_func_map = {
            # "<ctrl>+j": functools.partial(self.play_radio, path=self.ch2audio["jntm"])
            "<ctrl>+j": self.play_ngm
        }
        self.monitor = monitor.KeyBoardLister(on_press_func=self.on_press, on_release_func=self.on_release, hot_keys_func_map=hot_keys_func_map)
    
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
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPixelSize(35)
        font.setBold(True)
        self.lab_content.setFont(font)
        self.lab_content.setStyleSheet("color:black;")
        self.lab_content.move(38, 28)
        # self.lab_content.setText("123456")

        # 气泡框
        self.lab_bubble.move(0, 0)
        self.lab_bubble.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "bubble.png"))))
        
        # 坤人
        self.lab.move(50, 50)
        self.lab.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "cai1.png"))))

        
        # 设置窗口为 无边框 | 保持顶部显示
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint| QtCore.Qt.WindowType.WindowStaysOnTopHint)
        # # 设置窗口透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

    def play_radio(self, path):
        # print("path = ", path)
        playsound.playsound(path)
    
    def set_char(self, ch):
        if ch is None:
            return
        if ch in self.ch2audio:
            t = threading.Thread(target=self.play_radio, args=(self.ch2audio[ch],))
            # self.play_radio(self.ch2audio[ch])
            t.start()
        if ch == "j" or ch == "J":
            ch = "只因"

        # 设置字母
        if len(ch) == 1:
            # 显示字母
            font = QtGui.QFont()
            font.setFamily("微软雅黑")
            font.setPixelSize(35)
            font.setBold(True)
            self.lab_content.setFont(font)
            self.lab_content.setStyleSheet("color:black;")
            self.lab_content.move(40, 28)
        else:
            # 显示字母
            font = QtGui.QFont()
            font.setFamily("微软雅黑")
            font.setPixelSize(25)
            font.setBold(True)
            self.lab_content.setFont(font)
            self.lab_content.setStyleSheet("color:black;")
            self.lab_content.move(28, 28)
        self.lab_content.setText(ch)
        self.lab_content.adjustSize()
        # 张嘴
        self.lab.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "cai2.png"))))


    # 长时间没有触发则要回归到最初状态
    def reset_char(self):
        # print("reset char")
        # 设置字母
        self.lab_content.setText("")
        self.lab_content.adjustSize()
        # 闭嘴
        self.lab.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "cai1.png"))))


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

        quit_menu_qq = QtWidgets.QAction('更多', self, triggered=self.open_qq_group)
        tpMenu.addAction(quit_menu_qq)
        quit_menu = QtWidgets.QAction('退出', self, triggered=self.quit)
        tpMenu.addAction(quit_menu)

        mini_icon.setContextMenu(tpMenu)
        mini_icon.show()

    def quit(self):
        self.close()
        sys.exit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    pet = MainWidgets()
    sys.exit(app.exec_())