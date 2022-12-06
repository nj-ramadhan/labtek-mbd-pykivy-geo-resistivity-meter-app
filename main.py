import numpy as np
import kivy
import sys
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.config import Config
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import pyaudio

plt.style.use('bmh')
p = pyaudio.PyAudio()

Window.clearcolor = (.9, .9, .9, 1)
Window.fullscreen = 'auto'

from kivy.properties import ObjectProperty
import time

class SplashScreen(BoxLayout):
    screen_manager = ObjectProperty(None)
    monitor_screen = ObjectProperty(None)
    app_window = ObjectProperty(None)
    

    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_progress_bar, .1)

    def update_progress_bar(self, *args):
        if (self.ids.progress_bar.value + 2) < 100:
            raw_value = self.ids.progress_bar_label.text.split('[')[-1]
            value = raw_value[:-2]
            value = eval(value.strip())
            new_value = value + 2
            self.ids.progress_bar.value = new_value
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(new_value)
        else:
            self.ids.progress_bar.value = 100
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(100)
            time.sleep(2)
            self.screen_manager.current = 'main_screen'
            # self.resize_window(800, 600)
            # Window.borderless = False
            # Window.maximize()
            return False

    @staticmethod
    def resize_window(width=0, height=0):
        center0 = Window.center
        Window.size = (width, height)
        center1 = Window.center
        Window.left -= center1[0] - center0[0]
        Window.top -= center1[1] - center0[1]


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        
    # def __init__(self):
    #     super(MainScreen, self).__init__()
        # self.setting_screen()

    # def hide_widget(self, wid, dohide=True):
    #     if hasattr(wid, 'saved_attrs'):
    #         if not dohide:
    #             wid.height, wid.size_hint_x,  wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
    #             del wid.saved_attrs
    #     elif dohide:
    #         wid.saved_attrs = wid.height, wid.size_hint_x, wid.size_hint_y, wid.opacity, wid.disabled
    #         wid.height, wid.size_hint_x, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, None, 0, True

    # def setting_screen(self):
        # self.ids.layout_graph_carrier.add_widget(FigureCanvasKivyAgg(self.fig1))
        # self.ids.layout_graph_signal.clear_widgets()

        # self.hide_widget(self.ids.layout_setting, False)
        # self.hide_widget(self.ids.layout_graph, True)

        # self.ids.bt_screen_setting.disabled = True
        # self.ids.bt_screen_graph.disabled = False

        # self.ids.bt_update_graph.disabled = True

        # self.ids.label_page.text = "SETTING SCREEN"

class BSDSApp(App):
    def build(self):
        SplashScreen.resize_window(400, 300)
        Window.borderless = True
        Window.allow_screensaver = True

        screen = Builder.load_file('main.kv')

        return screen


if __name__ == '__main__':
    BSDSApp().run()