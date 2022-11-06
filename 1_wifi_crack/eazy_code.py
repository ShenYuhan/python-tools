import pywifi
import time

iface = pywifi.PyWiFi().interfaces()[0]
iface.scan()
print("Wifi疯狂扫描中, 请给博主点个赞点个关注等待1秒")
time.sleep(2)
profile = pywifi.Profile()
profile.ssid = "Ziroom-1002-5G"
with open("./wifi_crack/这里没有存密码.txt", "r") as fp:
    profile.key = fp.readline()
    print("密码是", profile.key)
profile.auth = pywifi.const.AUTH_ALG_OPEN
profile.akm.append(pywifi.const.AKM_TYPE_WPA2PSK)
profile.cipher = pywifi.const.CIPHER_TYPE_CCMP
iface.remove_all_network_profiles()
tmp_profile = iface.add_network_profile(profile)
iface.connect(tmp_profile)
time.sleep(2)
print("恭喜你已经连接上wifi ", profile.ssid, " 了！")