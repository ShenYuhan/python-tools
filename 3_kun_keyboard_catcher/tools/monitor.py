from pynput.keyboard import Listener, GlobalHotKeys, Key
class KeyBoardLister():
    def __init__(self, on_press_func, on_release_func, hot_keys_func_map=None):
        self.on_press = on_press_func
        self.on_release = on_release_func
        # 开启热键监控
        if hot_keys_func_map is not None:
            self.start_monitor_hotkey(hot_keys_func_map)
        self.start_monitor_keyboard()
        
    # 键盘监测
    def start_monitor_keyboard(self):
        self.listener = Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

    # 热键监控-非阻塞
    def start_monitor_hotkey(self, hot_keys_func_map):
        h = GlobalHotKeys(hot_keys_func_map)
        h.start()
