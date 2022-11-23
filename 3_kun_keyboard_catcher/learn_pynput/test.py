#-------------------------------------
# 测试控制鼠标
from pynput.mouse import Button, Controller
def testControllMouse():
    # 创建鼠标控制器
    mouse = Controller()

    # 读取位置
    print("The current posiont is {0}".format(mouse.position))

    # 直接移动
    mouse.position = (10, 20)
    print("Now we have moved it to {0}".format(mouse.position))

    # 相对移动
    mouse.move(5, -5)

    # 按下左键和松开
    mouse.press(Button.left)
    mouse.release(Button.left)

    # 双击
    mouse.click(Button.left, 2)

    # 鼠标滚轮
    mouse.scroll(0, 3)

#-------------------------------------
# 测试监控鼠标
from pynput.mouse import Listener
# 移动鼠标时
def on_move(x, y):
    # 鼠标移到屏幕最左上角时停止程序
    if x<1 and y<1:
        return False
    print("pointer moved to{0}".format((x, y)))

# 点击鼠标（按下或松开）时
def on_click(x, y, button, pressed):
    print("{0} at {1}".format("Pressed" if pressed else "Released", (x, y)))

# 滑动滚轮时
def on_scroll(x, y, dx, dy):
    print("Scrolled {0} at {1}".format("down" if dy<0 else "up", (x, y)))

# 启动监测鼠标
def start_monitor_mouse():
    # 方法1：阻塞，需要回调函数返回false或者使用mouse.Listener.stop
    with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        listener.join()
    # # 方法2：非阻塞，需要有一个主循环，否则会直接结束
    # listener = Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)
    # listener.start()

#---------------------------------------------
# 测试键盘控制
from pynput.keyboard import Key, Controller as k_Controller

def test_keyboard_contoll():
    import time
    # 给我5秒的时间打开个记事本来测试
    # 注意英文输入模式，否则会输入不全
    time.sleep(5)
    keyboard = k_Controller()

    # 按下和松开空格
    keyboard.press(Key.space)
    keyboard.release(Key.space)

    # 写个小a
    keyboard.press('a')
    keyboard.release('a')

    # 写个大A
    keyboard.press('A')
    keyboard.release('A')

    # 按下shift的同时摁a，那么就是写大A
    with keyboard.pressed(Key.shift):
        keyboard.press('a')
        keyboard.release('a')

    # 写个你好啊
    keyboard.type('你好啊老妹儿')

#-------------------------------------
# 测试监测键盘
from pynput.keyboard import Listener as k_Listener, GlobalHotKeys
# 按下时
def on_press(key):
    try:
        print("alphanueric jkey {} pressed".format(key.char))
    except AttributeError:
        print("spcial key {0} pressed".format(key))

# 松开键盘时
def on_release(key):
    print("{0} released".format(key))
    if key == Key.esc:
        # esc停止监测
        return False

# 开始监测键盘操作
def start_monitor_keyboard():
    # 阻塞方法
    with k_Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
    # # 非阻塞方法
    # listerner = k_Listener(on_press=on_press, on_release=on_release)
    # listener.start()

def on_activate_h():
    print("<ctrl>+<alt>+h pressed")

def on_activate_i():
    print("<ctrl>+<alt>+i pressed")

def on_activate_jntm():
    print("jntm pressed")

# 开启监测热键
def start_monitor_hotkey():
    h = GlobalHotKeys({
        "<ctrl>+<alt>+h": on_activate_h,
        "<ctrl>+<alt>+i": on_activate_i,
        "j+n+t+m":on_activate_jntm})
    h.start()


if __name__ == "__main__":
    # 测试鼠标控制
    # testControllMouse()
    # 启动鼠标监测
    # start_monitor_mouse()

    # 测试键盘控制
    # test_keyboard_contoll()
    # 测试键盘监测
    start_monitor_hotkey()
    start_monitor_keyboard()