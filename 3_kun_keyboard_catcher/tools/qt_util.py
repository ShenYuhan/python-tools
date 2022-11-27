#coding:utf-8
import functools
import sys
import os
from PyQt5 import QtGui, QtWidgets, QtCore
import monitor
from pynput.keyboard import Key
import playsound
import threading

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

        # 定时器，用于长时间不输入清空输入状态和闭嘴
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.reset_char)
        # 3秒定时清除文字
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
        }
        self.init_monitor()
        
        self.windowinit()
        self.icon_quit()

    # 版本提示
    def version_content(self):
        QtWidgets.QMessageBox.information(self, "坤音键盘v1.0", "抖音/B站：走神的阿圆 QQ群:766402914",
                                QtWidgets.QMessageBox.StandardButton.Yes)

    # 弹出提示
    def open_qq_group(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://jq.qq.com/?_wv=1027&k=A1DK3FhW'))

    # 松开键盘时
    def on_release(self, key):
        # self.lab_content.setText("")
        # self.lab_content.adjustSize()
        # 闭嘴
        self.lab.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "cai1.png"))))

    # 摁下键盘时
    def on_press(self, key):
        try:
            ch = key.char
        except AttributeError:
            ch = key.name
        self.set_char(ch)


    def init_monitor(self):
        hot_keys_func_map = {
            "<ctrl>+j": functools.partial(self.play_radio, path=self.ch2audio["jntm"])
            # "<ctrl>+j": self.play_ngm
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

        # 气泡框
        self.lab_bubble.move(0, 0)
        self.lab_bubble.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "bubble.png"))))
        
        # 坤人
        self.lab.move(50, 50)
        self.lab.setPixmap(QtGui.QPixmap(resource_path(os.path.join("imgs", "cai1.png"))))

        
        # 设置窗口为 无边框 | 保持顶部显示 | 任务栏不显示图标
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint| QtCore.Qt.WindowType.WindowStaysOnTopHint | QtCore.Qt.WindowType.SplashScreen)
        # # 设置窗口透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

    # 开线程放音乐，避免阻断主流程，实现可以同时放多个radio
    def play_radio(self, path):
        t = threading.Thread(target=playsound.playsound, args=(path,))
        t.start()
    
    def set_char(self, ch):
        if ch is None:
            return
        if ch in self.ch2audio:
            self.play_radio(self.ch2audio[ch])
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
        # 清除文字
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

        version_menu =  QtWidgets.QAction('作者', self, triggered=self.version_content)
        tpMenu.addAction(version_menu)
        quit_menu_qq = QtWidgets.QAction('QQ群', self, triggered=self.open_qq_group)
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