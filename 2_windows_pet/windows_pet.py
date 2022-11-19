import sys
import os
from functools import partial
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore, QtWidgets


class Qt_pet(QtWidgets.QWidget):

    def __init__(self):
        super(Qt_pet, self).__init__()

        self.dis_file = "img1"
        self.windowinit()
        self.icon_quit()

        self.pos_first = self.pos()
        self.timer = QTimer()
        self.timer.timeout.connect(self.img_update)
        self.timer.start(100)


    def img_update(self):
        if self.img_num < len(self.dir2img[self.current_dir])-1:
            self.img_num += 1
        else:
            self.img_num = 0
        self.qpixmap = QtGui.QPixmap(os.path.join(self.current_dir, self.dir2img[self.current_dir][self.img_num]))
        self.lab.setMaximumSize(self.pet_width, self.pet_height)
        self.lab.setScaledContents(True)
        # 重新设置lab的大小与图片保持一致
        self.lab.setGeometry(0, 0, self.qpixmap.width(), self.qpixmap.height())
        self.lab.setPixmap(self.qpixmap)

    
    # 获取放图片的路径，图片文件必须放在D:/Program Files (x86)/pet_conf/或者D:/Program Files/pet_conf/中，在里面放一个名为 imgN（比如img1，img2，img3的文件夹）的文件夹，文件夹中放具体的图片，图片的格式为N.png(比如1.png，2.png等)
    def get_conf_dir(self):
        conf_dirs = ["D:/Program Files (x86)/pet_conf/", "D:/Program Files/pet_conf/", "C:/Program Files/pet_conf/", "C:/Program Files (x86)/pet_conf/"]
        for conf_dir in conf_dirs:
            if os.path.exists(conf_dir) and os.path.isdir(conf_dir):
                self.conf_dir = conf_dir
                for root, dirs, files in os.walk(self.conf_dir):
                    if root in conf_dirs:
                        for dir in dirs:
                            for r, _, f in os.walk(os.path.join(root, dir)):
                                if r == os.path.join(root, dir) and len(f)>0:
                                    try:
                                        f.sort(key=lambda x: int(x.split(sep='.', maxsplit=1)[0]))
                                    except ValueError:
                                        f.sort(key=lambda x: x.split(sep='.', maxsplit=1)[0])
                                    self.dir2img.update({r: f})
                        return True
        QtWidgets.QMessageBox.warning(None, "警告", "没有找到配置文件！请查看使用说明", QtWidgets.QMessageBox.StandardButton.Ok)
        return False

    def windowinit(self):
        # 初始窗口设置大一点以免放入的图片显示不全
        self.pet_width = 1800
        self.pet_height = 1800
        # 获取桌面桌面大小决定宠物的初始位置为右上角
        desktop = QtWidgets.QApplication.desktop()
        self.x = desktop.width()-self.pet_width
        self.y = 100
        self.setGeometry(self.x, self.y, self.pet_width, self.pet_height)
        self.setWindowTitle('桌面宠物-by 走神的阿圆')
        self.img_num = 0
        # 找到配置文件，失败则退出
        self.dir2img = {}
        if not self.get_conf_dir():
            self.quit()
        
        self.lab = QtWidgets.QLabel(self)
        self.current_dir = list(self.dir2img.keys())[0]
        self.qpixmap = QtGui.QPixmap(os.path.join(self.current_dir, self.dir2img[self.current_dir][self.img_num]))
        self.lab.setPixmap(self.qpixmap)
        
        # 设置窗口为 无边框 | 保持顶部显示
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint| QtCore.Qt.WindowType.WindowStaysOnTopHint)
        # 设置窗口透明
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.show()

    # 设置系统托盘
    def icon_quit(self):
        mini_icon = QtWidgets.QSystemTrayIcon(self)
        mini_icon.setIcon(QtGui.QIcon(os.path.join(self.current_dir, self.dir2img[self.current_dir][0])))
        mini_icon.setToolTip("桌面宠物-by 走神的阿圆")
        # 1 toggle()、triggered()、clicked()区别
        # 这三个信号都是按钮点击后发射的信号，区别在于：
        # clicked()用于Button发射的信号
        # triggered()用于QAction发射的信号，原型：​​void triggered(bool checked = false);​​
        # toggle()用于ChekBox,非开即关，原型：​​void toggled(bool);​​
        quit_menu = QtWidgets.QAction('退出', self, triggered=self.quit)
        tpMenu = QtWidgets.QMenu(self)
        
        changeSubMenu = QtWidgets.QMenu(self)
        changeSubMenu.setTitle("切换")
        for dir in self.dir2img.keys():
            act = QtWidgets.QAction(os.path.basename(dir), self, triggered=partial(self.changeImg, dir))
            changeSubMenu.addAction(act)
        tpMenu.addMenu(changeSubMenu)
        tpMenu.addAction(quit_menu)
        mini_icon.setContextMenu(tpMenu)
        mini_icon.show()

    # 鼠标左键按下的时候获取当前位置
    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == QtCore.Qt.MouseButton.LeftButton:
            self.pos_first = QMouseEvent.globalPos() - self.pos()
            QMouseEvent.accept()
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.OpenHandCursor))

    # 拖动移动
    def mouseMoveEvent(self, QMouseEvent):
        self.move(QMouseEvent.globalPos() - self.pos_first)
        # self.x, self.y = self.pos().x, self.pos().y
        QMouseEvent.accept()

    def quit(self):
        self.close()
        sys.exit()

    def changeImg(self, dir):
        self.current_dir = dir


if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = Qt_pet()
    sys.exit(app.exec_())
