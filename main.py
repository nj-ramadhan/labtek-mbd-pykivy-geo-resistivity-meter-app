import numpy as np
import kivy
import sys
import os
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
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

plt.style.use('bmh')

Window.clearcolor = (.9, .9, .9, 1)
Window.fullscreen = 'auto'

colors = {
    "Red": {
        "200": "#EE2222",
        "500": "#EE2222",
        "700": "#EE2222",
    },

    "Blue": {
        "200": "#2222EE",
        "500": "#2222EE",
        "700": "#2222EE",
    },
    "Light": {
        "StatusBar": "E0E0E0",
        "AppBar": "#202020",
        "Background": "#EEEEEE",
        "CardsDialogs": "#FFFFFF",
        "FlatButtonDown": "#CCCCCC",
    },
}

from kivy.properties import ObjectProperty
import time

class ScreenSplash(BoxLayout):
    screen_manager = ObjectProperty(None)
    screen_main = ObjectProperty(None)
    app_window = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super(ScreenSplash, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_progress_bar, .01)

    def update_progress_bar(self, *args):
        if (self.ids.progress_bar.value + 1) < 100:
            raw_value = self.ids.progress_bar_label.text.split('[')[-1]
            value = raw_value[:-2]
            value = eval(value.strip())
            new_value = value + 1
            self.ids.progress_bar.value = new_value
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(new_value)
        else:
            self.ids.progress_bar.value = 100
            self.ids.progress_bar_label.text = 'Loading.. [{:} %]'.format(100)
            time.sleep(0.5)
            self.screen_manager.current = 'screen_main'
            return False

class ScreenMain(BoxLayout):
    screen_manager = ObjectProperty(None)
    app_window = ObjectProperty(None)

    checks_mode = []
    checks_config = []
    dt_mode = ""
    dt_config = ""

    flag_measure = False

    dt_distance = 0
    dt_time = 0
    dt_step = 10

    def __init__(self, **kwargs):
        super(ScreenMain, self).__init__(**kwargs)

    def hide_widget(self, wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.width, wid.height, wid.size_hint_x,  wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                # wid.height, wid.size_hint_x,  wid.size_hint_y = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.width, wid.height, wid.size_hint_x, wid.size_hint_y, wid.opacity, wid.disabled
            wid.width, wid.height, wid.size_hint_x, wid.size_hint_y, wid.opacity, wid.disabled = 0, 0, None, None, 0, True
            # wid.saved_attrs = wid.height, wid.size_hint_x, wid.size_hint_y
            # wid.height, wid.size_hint_x, wid.size_hint_y = 0, None, None

    def illustrate(self):
        self.hide_widget(self.ids.layout_illustration, False)

        self.dt_distance = self.ids.slider_distance.value
        self.dt_time = self.ids.slider_time.value
        self.dt_step = self.ids.slider_step.value

        offset = (self.dt_time + self.dt_distance) / 2
        amplitude = (self.dt_time - self.dt_distance) / 2

        x_axis = np.linspace(0, 100, int(10000/self.dt_step), endpoint=True) #20 data per periode in 100ms axis

        if("(SP) SELF POTENTIAL" in self.dt_mode):
            y_axis = offset + (4 * amplitude / self.dt_step) * np.abs((((x_axis - self.dt_step / 4) % self.dt_step) + self.dt_step) % self.dt_step - self.dt_step / 2 ) - amplitude
            data_adc = np.round(0.0 + (1.0 - 0.0) * ((y_axis - 160) / (360 - 160)) , 2)
            # print(y_axis)
        elif("(IP) INDUCED POLARIZATION" in self.dt_mode):
            y_axis = offset + (amplitude * np.sign (np.sin(2 * np.pi * 1 / self.dt_step * x_axis)))
            data_adc = np.round(0.0 + (1.0 - 0.0) * ((y_axis - 160) / (360 - 160)) , 2)
            # print(y_axis)
        elif("(R) RESISTIVITY" in self.dt_mode):
            y_axis = self.dt_distance + ((2 * amplitude / self.dt_step) * (x_axis % self.dt_step))
            data_adc = np.round(0.0 + (1.0 - 0.0) * ((y_axis - 160) / (360 - 160)) , 2)
            # print(y_axis)
        elif("(R+IP) COMBINATION" in self.dt_mode):
            y_axis = self.dt_distance + ((2 * amplitude / self.dt_step) * (x_axis % self.dt_step))
            data_adc = np.round(0.0 + (1.0 - 0.0) * ((y_axis - 160) / (360 - 160)) , 2)
            # print(y_axis)
        else:
            y_axis = 0 * x_axis
            data_adc = y_axis

        self.fig1, self.ax = plt.subplots()
        self.fig1.set_facecolor((.9,.9,.9))
        self.ax.set_facecolor((.9,.9,.9))
        self.ax.plot(x_axis, y_axis)

        self.ids.layout_illustration.clear_widgets()
        self.ids.layout_illustration.add_widget(FigureCanvasKivyAgg(self.fig1))

    def measure(self):
        if(self.flag_measure):
            self.stop_measure()
        else:
            self.flag_measure = True
            self.ids.bt_measure.text = "STOP MEASUREMENT"
            self.ids.bt_measure.md_bg_color = "red"

    def stop_measure(self):
        self.flag_measure = False
        self.ids.bt_measure.text = "RUN MEASUREMENT"
        self.ids.bt_measure.md_bg_color = "blue"
        print("measurement stopped")

    def checkbox_mode_click(self, instance, value, waves):
        if value == True:
            self.checks_mode.append(waves)
            modes = ''
            for x in self.checks_mode:
                modes = f'{modes} {x}'
            self.ids.output_mode_label.text = f'{modes} MODE CHOSEN'
        else:
            self.checks_mode.remove(waves)
            modes = ''
            for x in self.checks_mode:
                modes = f'{modes} {x}'
            self.ids.output_mode_label.text = ''
        
        self.dt_mode = modes

    def checkbox_config_click(self, instance, value, waves):
        if value == True:
            self.checks_config.append(waves)
            configs = ''
            for x in self.checks_config:
                configs = f'{configs} {x}'
            self.ids.output_config_label.text = f'{configs} CONFIGURATION CHOSEN'
        else:
            self.checks_config.remove(waves)
            configs = ''
            for x in self.checks_config:
                configs = f'{configs} {x}'
            self.ids.output_config_label.text = ''
        
        self.dt_config = configs

    def screen_setting(self):
        self.hide_widget(self.ids.layout_setting, False)
        self.hide_widget(self.ids.layout_data)
        self.hide_widget(self.ids.layout_graph)

        self.hide_widget(self.ids.layout_illustration)

    def screen_data(self):
        self.hide_widget(self.ids.layout_setting)
        self.hide_widget(self.ids.layout_data, False)
        self.hide_widget(self.ids.layout_graph)

        self.hide_widget(self.ids.layout_illustration)

        self.ids.layout_data.opacity = 1
        self.ids.layout_data.size_hint_x = 1
        self.ids.layout_data.size_hint_y = 0.5

    def screen_graph(self):
        self.hide_widget(self.ids.layout_setting)
        self.hide_widget(self.ids.layout_data)
        self.hide_widget(self.ids.layout_graph, False)

        self.hide_widget(self.ids.layout_illustration)

        self.ids.layout_graph.opacity = 1
        self.ids.layout_graph.size_hint_x = 1
        self.ids.layout_graph.size_hint_y = 0.5

class BSDSApp(MDApp):
    def build(self):
        # SplashScreen.resize_window(400, 300)
        self.theme_cls.colors = colors
        # self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        Window.borderless = True
        Window.allow_screensaver = True

        screen = Builder.load_file('main.kv')

        return screen


if __name__ == '__main__':
    BSDSApp().run()