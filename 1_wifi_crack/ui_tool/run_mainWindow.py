import sys

from PyQt5 import QtWidgets
import Ui_mainWindow
import wifi_utils

class MainWindowRun(Ui_mainWindow.Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindowRun, self).__init__(parent)
        self.setupUi(self)

        # 绑定按钮到事件
        self.pushButton.clicked.connect(self.ScanWifi)
        self.pushButton_2.clicked.connect(self.SetDict)
        self.pushButton_3.clicked.connect(self.StartLink)
        self.pushButton_3.setEnabled(False)

        # self.tableWidget.setRowCount(10)
        # self.tableWidget.setColumnCount(10)
        # self.tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("1111"))

    
    # 扫描周围wifi
    def ScanWifi(self):
        self.pushButton.setEnabled(False)
        results, err = wifi_utils.ScanWifi()
        # 如果已经连接上，弹出对话框提醒
        if err is not None:
            QtWidgets.QMessageBox.warning(None, "提醒", err, QtWidgets.QMessageBox.StandardButton.Ok)
            self.pushButton.setEnabled(True)
            return
        if len(results) == 0:
            QtWidgets.QMessageBox.warning(None, "提醒", "没有找到任何一个wifi", QtWidgets.QMessageBox.StandardButton.Ok)
            self.pushButton_3.setEnabled(False)
            self.pushButton.setEnabled(True)
            return
        # 如果还没连接上，打印当前扫描出来的全部wifi
        # 设置扫描wifi的表格
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(["Wifi名称"])
        self.tableWidget.setRowCount(len(results))
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        # self.tableWidget.setRowCount(10)
        # self.tableWidget.setColumnCount(10)

        for index in range(len(results)):
            item = QtWidgets.QTableWidgetItem(results[index])
            self.tableWidget.setItem(index, 0, item)
        self.pushButton_3.setEnabled(True)
        self.pushButton.setEnabled(True)
                

    # 设置密码字典
    def SetDict(self):
        # dir = QtWidgets.QFileDialog.getExistingDirectory()
        # 创建文件对话框
        dir = QtWidgets.QFileDialog()
        # 设置单选
        dir.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
        # 设置默认打开路径
        dir.setDirectory(".")
        # 设置能打开的文件类型
        dir.setNameFilter("密码文件(*.*)")
        # 判断是否选择了文件
        if dir.exec():
            self.lineEdit.setText(dir.selectedFiles()[0])

    # 开始链接wifi
    def StartLink(self):
        # 获取当前选中的项
        item = self.tableWidget.currentItem()
        if item is None:
            QtWidgets.QMessageBox.warning(None, "警告", "请先选择一个要连接的WIFI！", QtWidgets.QMessageBox.StandardButton.Ok)
            return
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        dict_file = self.lineEdit.text()
        self.statusbar.showMessage("开始破解密码中")
        info = wifi_utils.CrackAndLinkWifi(self, item.text(), ["123", "456", "789"], dict_file)
        QtWidgets.QMessageBox.warning(None, "通知", info, QtWidgets.QMessageBox.StandardButton.Ok)
        self.pushButton.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        return


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindowRun()
    mw.show()
    sys.exit(app.exec())