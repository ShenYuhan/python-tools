# coding:utf-8
import time
import pywifi

if __name__ == "__main__":
    wifi = pywifi.PyWiFi()
    print(wifi.interfaces())
    iface = wifi.interfaces()[0]
    print(dir(iface))
    # print(iface.status())
    # 关闭wifi
    # iface.disconnect()
    # time.sleep(1)
    # print(iface.status())
    print(len(iface.scan_results()))
    # iface.scan()
    for profile in iface.scan_results():
        # pass
        print("id=", profile.id, 
        " auth=", profile.auth, 
        " akm=", profile.akm, 
        " cipher=", profile.cipher, 
        # " ssid=", profile.ssid, 
        " ssid=", profile.ssid.encode("raw_unicode_escape").decode("utf-8"), 
        " bssid=", profile.bssid, 
        " key=", profile.key)

            
