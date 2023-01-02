### 0 文件目录
design.ui: qt-designer设计图  
main.py: 主文件  
requirments.txt: 编译依赖  
Ui_design.py: qt-designer ui编译python文件  


### 1 编译方法  
进入4_windows_waallpaper/，执行`pip install -r requirements.txt`安装依赖库  
进入到4_windows_waallpaper/中  
执行`pyinstaller -F -i yuan.ico -w .\main.py`生成可执行文件  

### 2 使用方法  
打开软件后先点击“选择视频”，选中视频后将在窗口播放。点击“预览”将展示壁纸效果，如果确认使用此壁纸，则点击“应用”，将会在C:\Program Files (x86)\yuan_wallpaper生成一个conf.json，内容为选中的视频参数，这样下次打开软件后将会自动播放。  