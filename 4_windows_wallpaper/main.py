import sys
import win32gui
import cv2
import os
import json

from PyQt5 import QtWidgets, QtCore, QtGui, QtMultimedia
import Ui_design

class TrayModel(QtWidgets.QSystemTrayIcon):
    def __init__(self, Window):
        super(TrayModel, self).__init__()
        self.window = Window
        self.init_ui()

    def init_ui(self):
        # 初始化菜单
        self.menu = QtWidgets.QMenu()

        self.manage_action = QtWidgets.QAction('打开主页面', self, triggered=self.activate_window)
        self.quit_action = QtWidgets.QAction('退出应用', self, triggered=self.quit_wallpaper)

        version_menu =  QtWidgets.QAction('作者', self, triggered=self.version_content)
        self.menu.addAction(version_menu)
        quit_menu_qq = QtWidgets.QAction('获取更多', self, triggered=self.open_qq_group)
        self.menu.addAction(quit_menu_qq)

        self.menu.addAction(self.manage_action)
        self.menu.addAction(self.quit_action)

        self.setContextMenu(self.menu)
        self.setToolTip("动态桌面-by走神的阿圆")

        self.setIcon(QtGui.QIcon('D:/program/python-tools/4_windows_wallpaper/yuan.ico'))
        self.icon = self.MessageIcon()

        self.activated.connect(self.app_click)

    # 版本提示
    def version_content(self):
        QtWidgets.QMessageBox.information(self.window, "动态桌面v0.1测试版", "抖音/B站：走神的阿圆 QQ群:766402914", QtWidgets.QMessageBox.StandardButton.Yes)
    
    # 弹出提示
    def open_qq_group(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl('https://jq.qq.com/?_wv=1027&k=A1DK3FhW'))

    def activate_window(self):
        self.window.showNormal()
        self.window.activateWindow()

    def quit_wallpaper(self):
        # 关闭通过0x052c打开的workerw层
        if self.window.worker_id != 0:
            win32gui.SendMessage(self.window.worker_id, 0x0010, 0, 0)  # WM_CLOSE
        QtWidgets.qApp.quit()

    def app_click(self, reason):
        if reason == self.ActivationReason.Trigger:
            self.window.showNormal()
            self.window.activateWindow()


class WallPaper(Ui_design.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, parent=None) -> None:
        super(WallPaper, self).__init__(parent)
        self.setupUi(self)

        # 打开视频
        self.pushButton.clicked.connect(self.OpenVideo)
        # 预览视频
        self.pushButton_2.clicked.connect(self.playVideo)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.clicked.connect(self.setWallPaper)
        self.pushButton_3.setEnabled(False)

        self.player = QtMultimedia.QMediaPlayer()
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.player.setVideoOutput(self.widget)
        self.player.setMuted(True)

        self.tray = TrayModel(self)
        self.tray.show()

        # 视频大小
        self.videoHeight = 0
        self.videoWidth = 0

        self.confDir = "C:/Program Files (x86)/yuan_wallpaper"
        self.confFile = "conf.json"
        self.conf = {}

        self.worker_id = 0

        # 如果配置文件有值则读取后自动设置壁纸
        if os.path.exists(os.path.join(self.confDir, self.confFile)):
            with open(os.path.join(self.confDir, self.confFile), 'r', encoding='utf-8') as fp:
                self.conf = json.load(fp)
                self.initWallPaper()
        
    # 根据显示器分辨率和视频大小确定显示尺寸，原则是没有黑边，即保证长宽相对较小的那个能占满显示器
    def get_wallpaper_size(self):
        desktopHeight = QtWidgets.QApplication.desktop().height()
        desktopWidth = QtWidgets.QApplication.desktop().width()
        # 宽度相比更小则保证宽度占满而拉伸长度
        if (self.videoWidth/desktopWidth) < (self.videoHeight/desktopHeight):
            return int(desktopWidth), int((desktopWidth/self.videoWidth)*self.videoHeight)
        else:
            return int((desktopHeight/self.videoHeight)*self.videoWidth), int(desktopHeight)

    # 打开视频
    def OpenVideo(self):
        # 创建文件对话框
        dir = QtWidgets.QFileDialog()
        # 设置单选
        dir.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        # 设置默认打开路径
        dir.setDirectory(".")
        # 设置能打开的文件类型
        dir.setNameFilter("视频文件(*.mp4 *.avi)")
        # 判断是否选择了文件
        if dir.exec():
            self.currentVideo = dir.selectedFiles()[0]
            self.lineEdit.setText(self.currentVideo)
            # 获取当前视频尺寸
            vcap = cv2.VideoCapture(self.currentVideo)
            self.videoHeight = vcap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.videoWidth = vcap.get(cv2.CAP_PROP_FRAME_WIDTH)
            content = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(self.currentVideo))
            # 清空之前的视频
            self.playlist.clear()
            self.playlist.addMedia(content)
            
            self.widget.show()
            
            self.player.play()
            self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.PlaybackMode.CurrentItemInLoop)
            
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)
            # self.widget.winId()

    def pretreatmentHandle(self):
        hwnd = win32gui.FindWindow("Progman", "Program Manager")
        win32gui.SendMessageTimeout(hwnd, 0x052C, 0, None, 0, 0x03E8)
        # return hwnd
        
        hwnd_WorkW = None
        while 1:
            hwnd_WorkW = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
            if not hwnd_WorkW:
                continue
            hView = win32gui.FindWindowEx(hwnd_WorkW, None, "SHELLDLL_DefView", None)
            if not hView:
                continue
            h = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
            break
            # 返回管理图标的worker层的下一个workerw层
        if h != 0:
            self.worker_id = h
            return h
            # while h:
            #     win32gui.SendMessage(h, 0x0010, 0, 0)  # WM_CLOSE
            #     h = win32gui.FindWindowEx(None, hwnd_WorkW, "WorkerW", None)
            # break
        return hwnd
    
    # 预览视频
    def playVideo(self):
        if self.playlist.isEmpty():
            QtWidgets.QMessageBox.warning(None, "警告", "请先选择视频", QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            hwnd = self.pretreatmentHandle()
            # 调整widget尺寸
            self.widget.show()
            # 将视频全屏
            # self.widget.setFullScreen(True)
            # self.widget.setGeometry(0, 0, self.videoWidth, self.videoHeight)
            w, h = self.get_wallpaper_size()
            self.widget.setGeometry(0, 0, w, h)
            video_h = int(self.widget.winId())
            # win32gui.SetParent(win_hwnd, hwnd)
            win32gui.SetParent(video_h, hwnd)
            self.pushButton_2.setText("取消")
            self.pushButton_2.clicked.disconnect()
            self.pushButton_2.clicked.connect(self.cancelPlayVideo)
            self.pushButton.setEnabled(False)
    
    # 取消预览
    def cancelPlayVideo(self):
        # self.widget.hide()
        self.widget.setGeometry(QtCore.QRect(40, 120, 711, 381))
        win_hwnd = int(self.winId())
        video_h = int(self.widget.winId())
        win32gui.SetParent(video_h, win_hwnd)
        self.pushButton_2.setText("预览")
        self.pushButton_2.clicked.disconnect()
        self.pushButton_2.clicked.connect(self.playVideo)
        self.pushButton.setEnabled(True)
        # 关闭通过0x052c打开的workerw层
        if self.worker_id != 0:
            win32gui.SendMessage(self.worker_id, 0x0010, 0, 0)  # WM_CLOSE

    # 初始化壁纸
    def initWallPaper(self):
        w = self.conf.get("widget_width", "")
        h = self.conf.get("widget_height", "")
        self.currentVideo = self.conf.get("video_path", "")
        if not w or not h or not self.currentVideo:
            return
        if not os.path.exists(self.currentVideo):
            QtWidgets.QMessageBox.warning(None, "警告", "视频 {} 不存在".format(self.currentVideo), QtWidgets.QMessageBox.StandardButton.Ok)
            return
        
        content = QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(self.currentVideo))
        # 清空之前的视频
        self.playlist.clear()
        self.playlist.addMedia(content)
        
        self.widget.show()
        
        self.player.play()
        self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.PlaybackMode.CurrentItemInLoop)
        self.widget.setGeometry(0, 0, w, h)
        video_h = int(self.widget.winId())
        hwnd = self.pretreatmentHandle()
        win32gui.SetParent(video_h, hwnd)

    # 应用壁纸
    def setWallPaper(self):
        if self.playlist.isEmpty():
            QtWidgets.QMessageBox.warning(None, "警告", "请先选择视频", QtWidgets.QMessageBox.StandardButton.Ok)
        else:
            hwnd = self.pretreatmentHandle()
            # 调整widget尺寸
            self.widget.show()
            # 将视频全屏
            w, h = self.get_wallpaper_size()
            self.widget.setGeometry(0, 0, w, h)
            video_h = int(self.widget.winId())
            win32gui.SetParent(video_h, hwnd)
            self.conf.update({"widget_width": w, "widget_height": h, "video_path": self.currentVideo})
            if not os.path.exists(self.confDir):
                os.makedirs(self.confDir)
            with open(os.path.join(self.confDir, self.confFile), 'w', encoding='utf-8') as fp:
                json.dump(self.conf, fp)
            
            QtWidgets.QMessageBox.information(None, "提示", "设置成功", QtWidgets.QMessageBox.StandardButton.Ok)

    def closeEvent(self, event):
        QtWidgets.QMessageBox.information(None, "提示", "最小化到托盘，要关闭请右键图标", QtWidgets.QMessageBox.StandardButton.Ok)
        event.ignore()
        self.hide()
        self.tray.show()



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    wall_paper = WallPaper()
    wall_paper.show()
    sys.exit(app.exec())