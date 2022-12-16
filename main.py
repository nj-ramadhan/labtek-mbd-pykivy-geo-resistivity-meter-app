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
from kivy.metrics import dp
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.figure import Figure
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.ticker import AutoMinorLocator
from kivymd.uix.datatables import MDDataTable

plt.style.use('bmh')

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

STEPS = 51
MAX_DISTANCE = 100
ELECTRODES_NUM = 48

y_electrode = np.zeros((4, STEPS))
x_electrode = np.zeros((4, STEPS))
n_electrode = np.zeros((ELECTRODES_NUM, STEPS))
c_electrode = np.array(["#FF0000","#FFDD00","#00FF00","#00FFDD"])
l_electrode = np.array(["C1","C2","P1","P2"])


class ScreenSplash(BoxLayout):
# class ScreenSplash(Screen):
    screen_manager = ObjectProperty(None)
    screen_setting = ObjectProperty(None)
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
            self.screen_manager.current = 'screen_setting'
            return False

class ScreenSetting(BoxLayout):
    screen_manager = ObjectProperty(None)

    checks_mode = []
    checks_config = []

    flag_measure = False

    dt_mode = ""
    dt_config = ""

    dt_distance = 0
    dt_constant = 10
    dt_time = 0
    dt_step = 0

    def __init__(self, **kwargs):
        super(ScreenSetting, self).__init__(**kwargs)

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
        self.dt_constant = self.ids.slider_constant.value
        self.dt_time = self.ids.slider_time.value
        self.dt_step = int(self.ids.slider_step.value)

        self.fig1, self.ax = plt.subplots()
        self.fig1.set_facecolor("#eeeeee")
        self.fig1.tight_layout(pad=3.0)

        # x_electrode = np.zeros((4,STEPS))
        self.ids.layout_illustration.remove_widget(FigureCanvasKivyAgg(self.fig1))

        if("WENNER" in self.dt_config):
            x_electrode[0, self.dt_step] = self.dt_distance * self.dt_step
            x_electrode[1, self.dt_step] = self.dt_distance + x_electrode[0, self.dt_step]
            x_electrode[2, self.dt_step] = self.dt_distance + x_electrode[1, self.dt_step]
            x_electrode[3, self.dt_step] = self.dt_distance + x_electrode[2, self.dt_step]
            self.ax.set_xlim([-2, MAX_DISTANCE])

        elif("SCHLUMBERGER" in self.dt_config):
            x_electrode[0, self.dt_step] = -0.5 *  self.dt_distance
            x_electrode[1, self.dt_step] = 0.5 * self.dt_distance
            x_electrode[2, self.dt_step] = -0.5 * self.dt_distance * self.dt_constant
            x_electrode[3, self.dt_step] = 0.5 * self.dt_distance * self.dt_constant
            self.ax.set_xlim([-MAX_DISTANCE/2, MAX_DISTANCE/2])

        elif("DIPOLE-DIPOLE" in self.dt_config):
            x_electrode[0, self.dt_step] = 0
            x_electrode[1, self.dt_step] = self.dt_distance + x_electrode[0, self.dt_step]
            x_electrode[2, self.dt_step] = self.dt_constant + x_electrode[1, self.dt_step]
            x_electrode[3, self.dt_step] = self.dt_distance + x_electrode[2, self.dt_step]
            self.ax.set_xlim([-2, MAX_DISTANCE])

        else:
            pass

        if("(SP) SELF POTENTIAL" in self.dt_mode):
            n_electrode[0, self.dt_step] = 0 #none
            n_electrode[1, self.dt_step] = 0 #none
            n_electrode[2, self.dt_step] = 3 #p1
            n_electrode[3, self.dt_step] = 4 #p2

        elif("(IP) INDUCED POLARIZATION" in self.dt_mode):
            n_electrode[0, self.dt_step] = 1 #c1
            n_electrode[1, self.dt_step] = 2 #c2
            n_electrode[2, self.dt_step] = 3 #p1
            n_electrode[3, self.dt_step] = 4 #p2

        elif("(R) RESISTIVITY" in self.dt_mode):
            n_electrode[0, self.dt_step] = 1 #c1
            n_electrode[1, self.dt_step] = 2 #c2
            n_electrode[2, self.dt_step] = 3 #p1
            n_electrode[3, self.dt_step] = 4 #p2

        elif("(R+IP) COMBINATION" in self.dt_mode):
            n_electrode[0, self.dt_step] = 1 #c1
            n_electrode[1, self.dt_step] = 2 #c2
            n_electrode[2, self.dt_step] = 3 #p1
            n_electrode[3, self.dt_step] = 4 #p2
            
        else:
            pass

        self.ax.set_facecolor("#eeeeee")
        self.ax.scatter(x_electrode[0, self.dt_step], y_electrode[0, self.dt_step], c=c_electrode[0], label=l_electrode[0], marker=7, s=100)
        self.ax.scatter(x_electrode[1, self.dt_step], y_electrode[1, self.dt_step], c=c_electrode[1], label=l_electrode[1], marker=7, s=100)
        self.ax.scatter(x_electrode[2, self.dt_step], y_electrode[2, self.dt_step], c=c_electrode[2], label=l_electrode[2], marker=7, s=100)
        self.ax.scatter(x_electrode[3, self.dt_step], y_electrode[3, self.dt_step], c=c_electrode[3], label=l_electrode[3], marker=7, s=100)
        self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Electrode")
        self.ax.set_xlabel('distance (m)')
        # self.ax.xaxis.set_minor_locator(AutoMinorLocator(2))
        # self.ax.yaxis.set_minor_locator(AutoMinorLocator(2))
        self.ax.grid(which='minor', linewidth=0.6, color="#000000")

        self.ids.layout_illustration.clear_widgets()
        self.ids.layout_illustration.add_widget(FigureCanvasKivyAgg(self.fig1))
        print(n_electrode)

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
        self.screen_manager.current = 'screen_setting'

    def screen_data(self):
        self.screen_manager.current = 'screen_data'

    def screen_graph(self):
        self.screen_manager.current = 'screen_graph'

class ScreenData(BoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenData, self).__init__(**kwargs)

    def data(self):
        layout = self.ids.layout_tables
        
        data_tables = MDDataTable(
            use_pagination=True,
            column_data=[
                ("No.", dp(30)),
                ("Column 1", dp(30)),
                ("Column 2", dp(30)),
                ("Column 3", dp(30)),
                ("Column 4", dp(30)),
                ("Column 5", dp(30)),
            ],
            row_data=[
                (f"{i + 1}", "1", "2", "3", "4", "5") for i in range(50)
            ],
        )

        layout.remove_widget(data_tables)
        layout.add_widget(data_tables)

    def screen_setting(self):
        self.screen_manager.current = 'screen_setting'

    def screen_data(self):
        self.screen_manager.current = 'screen_data'

    def screen_graph(self):
        self.screen_manager.current = 'screen_graph'

class ScreenGraph(BoxLayout):
    screen_manager = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ScreenGraph, self).__init__(**kwargs)

    def screen_setting(self):
        self.screen_manager.current = 'screen_setting'

    def screen_data(self):
        self.screen_manager.current = 'screen_data'

    def screen_graph(self):
        self.screen_manager.current = 'screen_graph'

class BSDSApp(MDApp):
    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Blue"
        Window.fullscreen = 'auto'
        Window.borderless = True
        Window.allow_screensaver = True
        self.icon = 'asset/logo_labtek_p.ico'

        screen = Builder.load_file('main.kv')

        return screen


if __name__ == '__main__':
    BSDSApp().run()