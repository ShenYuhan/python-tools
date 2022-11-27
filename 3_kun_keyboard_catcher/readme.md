编译方法  
进入3_kun_keyboard_catcher，执行`pip install -r requirements.txt`安装依赖库  
进入到3_kun_keyboard_catcher/tools/中  
执行`pyi-makespec -F -i .\imgs\kun_keyboard.ico -w .\qt_util.py`以生成spec文件  
修改spec文件中`datas=[('audios','audios'),('imgs','imgs')],`一行，audios，imgs为主函数所在文件同级目录  
修改完之后执行`pyinstaller .\qt_util.spec`就可以生成可执行文件  


v1.1  
 - 解决windows下由于playsound库使用utf8编码导致无法正常播放音频的问题  

v1.2
 - 任务栏不再显示图标
 - 精修声音资源，减少延迟
