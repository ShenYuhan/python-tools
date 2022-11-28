### 0 文件目录
tools是工具目录  
learn_pynput是pynput demo  

### 1 编译方法  
进入3_kun_keyboard_catcher/tools/，执行`pip install -r requirements.txt`安装依赖库，注意playsound库版本最好是1.2.2  
进入到3_kun_keyboard_catcher/tools/中  
执行`pyi-makespec -F -i .\imgs\kun_keyboard.ico -w .\qt_util.py`以生成spec文件  
修改spec文件中`datas=[('audios','audios'),('imgs','imgs')],`一行，audios，imgs为主函数所在文件同级目录  
修改完之后执行`pyinstaller .\qt_util.spec`就可以生成可执行文件  

如果是自己编译，其中的playsound库中源代码要改一下
```python
def winCommand(*command):
        buf = c_buffer(255)
        # 原始源文件中使用getfilesystemencoding()获取编码方式，在windows下会返回utf，实际上windows要使用gbk，因此下面这行改成我这里的样子
        command = ' '.join(command).encode(getfilesystemencoding() if sys.platform != "win32" else "gbk")
        errorCode = int(windll.winmm.mciSendStringA(command, buf, 254, 0))
        if errorCode:
            errorBuffer = c_buffer(255)
            windll.winmm.mciGetErrorStringA(errorCode, errorBuffer, 254)
            exceptionMessage = ('\n    Error ' + str(errorCode) + ' for command:'
                                '\n        ' + command.decode() +
                                '\n    ' + errorBuffer.value.decode())
            raise PlaysoundException(exceptionMessage)
        return buf.value
```

### 2 版本迭代

v1.2
 - 任务栏不再显示图标
 - 精修声音资源，减少延迟

v1.1  
 - 解决windows下由于playsound库使用utf8编码导致无法正常播放音频的问题  


