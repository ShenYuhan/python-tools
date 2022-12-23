### 0 文件目录
design.ui: qt-designer设计图  
main.py: 主文件  
requirments.txt: 编译依赖  
Ui_design.py: qt-designer ui编译python文件  


### 1 编译方法  
进入4_windows_waallpaper/，执行`pip install -r requirements.txt`安装依赖库  
进入到4_windows_waallpaper/中  
执行`pyinstaller -F -i yuan.ico -w .\main.py`生成可执行文件  
