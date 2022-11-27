编译方法  
进入3_kun_keyboard_catcher，执行`pip install -r requirements.txt`安装依赖库  
进入到3_kun_keyboard_catcher/tools/中  
执行`pyi-makespec -F -i .\imgs\kun_keyboard.ico -w .\qt_util.py`以生成spec文件  
修改spec文件中`datas=[('audios','audios'),('imgs','imgs')],`一行，audios，imgs为主函数所在文件同级目录  
修改完之后执行`pyinstaller .\qt_util.spec`就可以生成可执行文件  