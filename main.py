from kivy.config import Config
Config.set('kivy', 'keyboard_mode', 'systemanddock')
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.uix.screenmanager import ScreenManager
from kivymd.toast import toast
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.datatables import MDDataTable
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os, sys, time, numpy as np
from datetime import datetime
import minimalmodbus, configparser, serial, logging
from serial.tools import list_ports
np.set_printoptions(threshold=sys.maxsize)
plt.style.use('bmh')
# Suppress Matplotlib font-related warnings
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

colors = {
    "Red": {"200": "#EE2222","500": "#EE2222","700": "#EE2222",},
    "Blue": {"200": "#196BA5","500": "#196BA5","700": "#196BA5",},
    "Light": {"StatusBar": "E0E0E0","AppBar": "#202020","Background": "#EEEEEE","CardsDialogs": "#FFFFFF","FlatButtonDown": "#CCCCCC",},
    "Dark": {"StatusBar": "101010","AppBar": "#E0E0E0","Background": "#111111","CardsDialogs": "#000000","FlatButtonDown": "#333333",},
}

config_name = 'config.ini'
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    running_mode = 'Frozen/executable'
else:
    try:
        app_full_path = os.path.realpath(__file__)
        application_path = os.path.dirname(app_full_path)
        running_mode = "Non-interactive (e.g. 'python myapp.py')"
    except NameError:
        application_path = os.getcwd()
        running_mode = 'Interactive'

config_full_path = os.path.join(application_path, config_name)
config = configparser.ConfigParser()
config.read(config_full_path)

DEBUG = bool(int(config['setting']['DEBUG']))
DONGLE_DIR_LIN = config['setting']['DONGLE_DIR_LIN']
DONGLE_DIR_WIN = config['setting']['DONGLE_DIR_WIN']
USERNAME = config['setting']['USERNAME']
SERIAL_NUMBER = config['setting']['SERIAL_NUMBER']
if platform == "linux":    
    DISK_ADDRESS = os.path.join("/media/", USERNAME)
    DISK_ADDRESS = os.path.join(DISK_ADDRESS, DONGLE_DIR_LIN)
elif platform == "win":    
    DISK_ADDRESS = os.path.dirname(DONGLE_DIR_WIN)

COM_PORT_MCU = config['setting']['COM_PORT_MCU']
COM_PORT_RTU = config['setting']['COM_PORT_RTU']

STEPS = 51
MAX_POINT = 10000
ELECTRODES_NUM = 48

PIN_ENABLE = 23 #16
PIN_POLARITY = 24 #18

C_OFFSET = 2.5412
C_GAIN = 5.0 * 1000.0 #channge from A to mA with gain

P_OFFSET = 0.001
P_GAIN = 1.0
# SHUNT_OHMS = 0.1
# MAX_EXPECTED_AMPS = 0.1
# 
# PIN_FWD = 16
# PIN_REV = 18

BAUDRATE = 9600
BYTESIZE = 8
PARITY = serial.PARITY_NONE
STOPBIT = 1
TIMEOUT = 0.5

BAUDRATE_RTU = 19200
BYTESIZE_RTU = 8
PARITY_RTU = serial.PARITY_NONE
STOPBIT_RTU = 2
TIMEOUT_RTU = 0.05

REQUEST_TIME_OUT = float(config['setting']['REQUEST_TIME_OUT'])
DELAY_INITIAL = int(config['setting']['DELAY_INITIAL'])
UPDATE_INTERVAL = int(config['setting']['UPDATE_INTERVAL'])
UPDATE_INTERVAL_GRAPH = int(config['setting']['UPDATE_INTERVAL_GRAPH'])
GRAPH_STATE_COUNT = int(config['setting']['GRAPH_STATE_COUNT'])
DONGLE_MOUNT_MAX_RETRY = int(config['setting']['DONGLE_MOUNT_MAX_RETRY'])

x_electrode = np.zeros((4, MAX_POINT))
n_electrode = np.zeros((ELECTRODES_NUM, STEPS))
c_electrode = np.array(["#196BA5","#FF0000","#FFDD00","#00FF00","#00FFDD"])
l_electrode = np.array(["Datum","C1","C2","P1","P2"])
arr_electrode = np.zeros([4, 0])
data_base = np.zeros([5, 0])
data_electrode = np.zeros([4, 0], dtype=int)
data_pos = np.zeros([2, 0])

checks_mode = []
checks_config = []
dt_mode = ""
dt_config = ""
dt_distance = 1
dt_constant = 1
real_constant = 1
dt_time = 500
dt_cycle = 1
dt_threshold = 20.0

dt_measure = np.zeros(6)
dt_current = np.zeros(10)
dt_voltage = np.zeros(10)
flag_run = False
flag_run_prev = False
flag_measure = False
flag_dongle = True
flag_autosave_data = False
flag_autosave_graph = False

data_rtu = np.zeros([216, 0], dtype=int)
data_rtu1 = np.zeros(36, dtype=int)
data_rtu2 = np.zeros(36, dtype=int)
data_rtu3 = np.zeros(36, dtype=int)
data_rtu4 = np.zeros(36, dtype=int)
data_rtu5 = np.zeros(36, dtype=int)
data_rtu6 = np.zeros(36, dtype=int)

step = 0
max_step = 1

count_mounting = 0
inject_state = 0
graph_state = 0

class ScreenSplash(MDScreen):    
    def __init__(self, **kwargs):
        super(ScreenSplash, self).__init__(**kwargs)
        if platform == "linux":
            try:
                os.system('cmd /c "cd /media"')
                os.system('cmd /c "sudo rm -r /labtek"')
            except:
                pass
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

class ScreenSetting(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenSetting, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init)
        Clock.schedule_interval(self.regular_check, 1)

    def regular_check(self, dt):
        global flag_run
        if(flag_run):
            self.ids.bt_measure.text = "STOP MEASUREMENT"
            self.ids.bt_measure.md_bg_color = "#A50000"
        else:
            self.ids.bt_measure.text = "RUN MEASUREMENT"
            self.ids.bt_measure.md_bg_color = "#196BA5"

    def delayed_init(self, dt):
        global rtu1, rtu2, rtu3, rtu4, rtu5, rtu6
        global data_rtu1, data_rtu2, data_rtu3, data_rtu4, data_rtu5, data_rtu6

        self.ids.bt_shutdown.md_bg_color = "#A50000"
        self.ids.mode_ves.active = True

        self.fig, self.ax = plt.subplots()
        self.fig.set_facecolor("#eeeeee")
        self.fig.tight_layout()
        l, b, w, h = self.ax.get_position().bounds
        self.ax.set_position(pos=[l, b + 0.3*h, w, h*0.7])
        
        self.ax.set_xlabel("distance [m]", fontsize=10)
        self.ax.set_ylabel("n", fontsize=10)

        self.ids.layout_illustration.add_widget(FigureCanvasKivyAgg(self.fig))

        try:
            ports = list_ports.comports(include_links=False)
            for port in ports :
                com_port_rtu = COM_PORT_RTU
                toast("switching box is connected to " + com_port_rtu)
                print("switching box is connected to " + com_port_rtu)

            rtu1 = minimalmodbus.Instrument(com_port_rtu, 1 ,mode=minimalmodbus.MODE_RTU)
            rtu2 = minimalmodbus.Instrument(com_port_rtu, 2 ,mode=minimalmodbus.MODE_RTU)
            rtu3 = minimalmodbus.Instrument(com_port_rtu, 3 ,mode=minimalmodbus.MODE_RTU)
            rtu4 = minimalmodbus.Instrument(com_port_rtu, 4 ,mode=minimalmodbus.MODE_RTU)
            rtu5 = minimalmodbus.Instrument(com_port_rtu, 5 ,mode=minimalmodbus.MODE_RTU)
            rtu6 = minimalmodbus.Instrument(com_port_rtu, 6 ,mode=minimalmodbus.MODE_RTU)

            rtu1.write_bits(80, data_rtu1.tolist()) 
            rtu2.write_bits(80, data_rtu2.tolist()) 
            rtu3.write_bits(80, data_rtu3.tolist()) 
            rtu4.write_bits(80, data_rtu4.tolist()) 
            rtu5.write_bits(80, data_rtu5.tolist()) 
            rtu6.write_bits(80, data_rtu6.tolist()) 

        except:
            toast("no switching box connected")
            print("no switching box connected")

        try:
            self.connect_to_mcu()
            Clock.schedule_interval(self.read_mcu, REQUEST_TIME_OUT)
            toast("Switching unit is sucessfully connected")
        except:
            Clock.schedule_interval(self.auto_reconnect, REQUEST_TIME_OUT)
            toast("Switching unit is disconnected")

        # try:
        #     com_port_mcu.write(b"%") # reset switching
        #     data_reset = com_port_mcu.readline().decode("utf-8").strip()  # read the incoming data and remove newline character
        #     while True:
        #         print(data_reset)
        #         if data_reset == "Semua decoder mati":
        #             break
        #         else:
        #             com_port_mcu.write(b"%") # reset switching
        #             data_reset = com_port_mcu.readline().decode("utf-8").strip()

        # except:
        #     toast("No Switching Unit connected")
            # print("no switching unit connected")

    def auto_reconnect(self, dt):
        try:
            self.connect_to_mcu()
            Clock.schedule_interval(self.read_mcu, REQUEST_TIME_OUT)
            Clock.unschedule(self.auto_reconnect)
        except:
            toast("Switching unit is disconnected, try reconnecting..")

    def read_mcu(self, dt):
        global com_port_mcu
        global dt_threshold

        if(not DEBUG):
            try:
                print("Reading mcu")
                com_port_mcu.write(b" ")
            except Exception as e:
                Clock.schedule_interval(self.auto_reconnect, REQUEST_TIME_OUT)
                error_msg = "Error reading Switching unit :" + str(e)
                print(error_msg)

    def connect_to_mcu(self):
        global com_port_mcu

        if(not DEBUG):
            try:
                com_port_mcu = serial.Serial(COM_PORT_MCU)  # COM to Microcontroller, checked manually
                com_port_mcu.baudrate = BAUDRATE
                com_port_mcu.parity = PARITY
                com_port_mcu.bytesize = BYTESIZE
                toast("Sucessfully connect to Switching unit")
            except Exception as e:
                error_msg = "Error connect to Switching unit :" + str(e)
                print(error_msg)
                toast("Error connect to Switching unit, try reconnecting")

    def illustrate(self):
        global dt_mode
        global dt_config
        global dt_distance
        global dt_constant
        global dt_time
        global dt_cycle
        global x_datum
        global y_datum
        global data_pos
        global data_rtu
        global max_step
        global arr_electrode

        dt_distance = self.ids.slider_distance.value
        dt_constant = self.ids.slider_constant.value
        dt_time = int(self.ids.slider_time.value)
        dt_cycle = int(self.ids.slider_cycle.value)

        self.fig, self.ax = plt.subplots()
        self.ids.layout_illustration.remove_widget(FigureCanvasKivyAgg(self.fig))
        x_datum = np.zeros(MAX_POINT)
        y_datum = np.zeros(MAX_POINT)
        x_electrode = np.zeros((4, MAX_POINT))

        if("WENNER (ALPHA)" in dt_config):
            num_step = 0
            num_trial = 1
            for multiplier in range(dt_constant):
                for pos_el in range(ELECTRODES_NUM - 3 * num_trial):
                    x_electrode[0, num_step] = pos_el
                    x_electrode[1, num_step] = num_trial + x_electrode[0, num_step]
                    x_electrode[2, num_step] = num_trial + x_electrode[1, num_step]
                    x_electrode[3, num_step] = num_trial + x_electrode[2, num_step]
                    x_datum[num_step] = (x_electrode[1, num_step] + (x_electrode[2, num_step] - x_electrode[1, num_step])/2) * dt_distance
                    y_datum[num_step] = (multiplier + 1) * dt_distance
                    
                    num_step += 1

                num_trial += 1

        elif("WENNER (BETA)" in dt_config):
            num_step = 0
            num_trial = 1
            for multiplier in range(dt_constant):
                for pos_el in range(ELECTRODES_NUM - 3 * num_trial):
                    x_electrode[0, num_step] = pos_el
                    x_electrode[1, num_step] = num_trial + x_electrode[0, num_step]
                    x_electrode[2, num_step] = num_trial + x_electrode[1, num_step]
                    x_electrode[3, num_step] = num_trial + x_electrode[2, num_step]
                    x_datum[num_step] = (x_electrode[1, num_step] + (x_electrode[2, num_step] - x_electrode[1, num_step])/2) * dt_distance
                    y_datum[num_step] = (multiplier + 1) * dt_distance
                    
                    num_step += 1

                num_trial += 1

        if("WENNER (GAMMA)" in dt_config):
            num_step = 0
            num_trial = 1
            for multiplier in range(dt_constant):
                for pos_el in range(ELECTRODES_NUM - 3 * num_trial):
                    x_electrode[0, num_step] = pos_el
                    x_electrode[1, num_step] = num_trial + x_electrode[0, num_step]
                    x_electrode[2, num_step] = num_trial + x_electrode[1, num_step]
                    x_electrode[3, num_step] = num_trial + x_electrode[2, num_step]
                    x_datum[num_step] = (x_electrode[1, num_step] + (x_electrode[2, num_step] - x_electrode[1, num_step])/2) * dt_distance
                    y_datum[num_step] = (multiplier + 1) * dt_distance
                    
                    num_step += 1

                num_trial += 1

        elif("SCHLUMBERGER" in dt_config):
            num_step = 0
            num_trial = 1
            for multiplier in range(dt_constant):
                for pos_el in range(ELECTRODES_NUM - 3 * num_trial):
                    x_electrode[0, num_step] = pos_el
                    x_electrode[1, num_step] = num_trial + x_electrode[0, num_step]
                    x_electrode[2, num_step] = num_trial + x_electrode[1, num_step]
                    x_electrode[3, num_step] = num_trial + x_electrode[2, num_step]
                    x_datum[num_step] = (x_electrode[1, num_step] + (x_electrode[2, num_step] - x_electrode[1, num_step])/2) * dt_distance
                    y_datum[num_step] = (multiplier + 1) * dt_distance
                    
                    num_step += 1

                num_trial += 1

        elif("DIPOLE-DIPOLE" in dt_config):
            nmax_available = 0
            if(ELECTRODES_NUM % 2) != 0:
                if(dt_constant > (ELECTRODES_NUM - 3) / 2):
                    nmax_available = (ELECTRODES_NUM - 3) / 2
                else:
                    nmax_available = dt_constant
            else:
                if(dt_constant > (ELECTRODES_NUM - 3) / 2):
                    nmax_available = round((ELECTRODES_NUM - 3) / 2)
                else:
                    nmax_available = dt_constant

            num_datum = 0
            count_datum = 0      
            for i in range(nmax_available):
                for j in range(ELECTRODES_NUM - 1 - i * 2):
                    num_datum = num_datum + j
                count_datum = count_datum + num_datum
                num_datum = 0     

            num_step = 0
            num_trial = 0
            for i in range(nmax_available):
                for j in range(ELECTRODES_NUM - 1 - i * 2):
                    for k in range(ELECTRODES_NUM - i * 2 - j - 1):
                        x_electrode[1, num_step] = j - 1
                        x_electrode[0, num_step] = j + (i - 2)
                        x_electrode[2, num_step] = num_trial + 2 + x_electrode[0, num_step]
                        x_electrode[3, num_step] = i + 1 + x_electrode[2, num_step]
                        x_datum[num_step] = (x_electrode[0, num_step] + (x_electrode[2, num_step] - x_electrode[0, num_step])/2) * dt_distance
                        y_datum[num_step] = (i + 1) * dt_distance
                        
                        num_step += 1
                        num_trial += 1

                    num_trial = 0
        else:
            x_electrode[0,0] = 0
            x_electrode[1,0] = 1
            x_electrode[2,0] = 2
            x_electrode[3,0] = 3

        try:
            max_step = np.trim_zeros(x_electrode[1,:]).size

            data_c1 = x_electrode[0,:max_step]
            data_p1 = x_electrode[1,:max_step]
            data_p2 = x_electrode[2,:max_step]
            data_c2 = x_electrode[3,:max_step]

            arr_electrode = np.array([data_c1, data_p1, data_p2, data_c2], dtype=int)
            print(arr_electrode.T)

            data_rtu = np.zeros([216,max_step], dtype=int)
            for i in range(max_step):
                data_rtu[arr_electrode[0,i]*4, i] = 1
                data_rtu[arr_electrode[1,i]*4 + 1, i] = 1
                data_rtu[arr_electrode[2,i]*4 + 2, i] = 1
                data_rtu[arr_electrode[3,i]*4 + 3, i] = 1
            # print(data_rtu.T)

        except:
            print("error simulating")
            toast("error simulating")

        self.fig.set_facecolor("#eeeeee")
        self.fig.tight_layout()
        l, b, w, h = self.ax.get_position().bounds
        self.ax.set_position(pos=[l, b + 0.3*h, w*0.9, h*0.7])
        self.ax.set_xlabel("distance [m]", fontsize=10)
        self.ax.set_ylabel("n", fontsize=10)
       
        self.ax.set_facecolor("#eeeeee")
        
        x_data = np.trim_zeros(x_datum)
        y_data = np.trim_zeros(y_datum)
        # x_data = x_datum[np.array([x.size>0 for x in x_datum])]
        # y_data = y_datum[np.array([y.size>0 for y in y_datum])]
        data_pos = np.array([x_data, y_data])

        #datum location
        self.ax.scatter(x_data, y_data, c=c_electrode[0], label=l_electrode[0], marker='.')

        #electrode location
        self.ax.scatter(x_electrode[0,0]*dt_distance , 0, c=c_electrode[1], label=l_electrode[1], marker=7)
        self.ax.scatter(x_electrode[1,0]*dt_distance , 0, c=c_electrode[2], label=l_electrode[2], marker=7)
        self.ax.scatter(x_electrode[2,0]*dt_distance , 0, c=c_electrode[3], label=l_electrode[3], marker=7)
        self.ax.scatter(x_electrode[3,0]*dt_distance , 0, c=c_electrode[4], label=l_electrode[4], marker=7)

        self.ax.invert_yaxis()
        self.ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Electrode")         
        self.ids.layout_illustration.clear_widgets()
        self.ids.layout_illustration.add_widget(FigureCanvasKivyAgg(self.fig))

    def measure(self):
        global flag_run

        if(flag_run):
            flag_run = False
        else:
            flag_run = True

    def checkbox_mode_click(self, instance, value, waves):
        global checks_mode
        global dt_mode
        
        if value == True:
            checks_mode.append(waves)
            modes = ''
            for x in checks_mode:
                modes = f'{modes} {x}'
            self.ids.output_mode_label.text = f'{modes} MODE CHOSEN'
        else:
            checks_mode.remove(waves)
            modes = ''
            for x in checks_mode:
                modes = f'{modes} {x}'
            self.ids.output_mode_label.text = ''
        
        dt_mode = modes

    def checkbox_config_click(self, instance, value, waves):
        global checks_config
        global dt_config

        if value == True:
            checks_config.append(waves)
            configs = ''
            for x in checks_config:
                configs = f'{configs} {x}'
            self.ids.output_config_label.text = f'{configs} CONFIGURATION CHOSEN'
        else:
            checks_config.remove(waves)
            configs = ''
            for x in checks_config:
                configs = f'{configs} {x}'
            self.ids.output_config_label.text = ''
        
        dt_config = configs

    def threshold_up(self):
        global dt_threshold
        if(dt_threshold < 200):
            dt_threshold += 5
            self.ids.lb_volt_threshold.text = str(dt_threshold)

    def threshold_down(self):
        global dt_threshold
        if(dt_threshold > 20):
            dt_threshold -= 5
            self.ids.lb_volt_threshold.text = str(dt_threshold)

    def screen_setting(self):
        self.screen_manager.current = 'screen_setting'

    def screen_data(self):
        self.screen_manager.current = 'screen_data'

    def screen_graph(self):
        self.screen_manager.current = 'screen_graph'

    def exec_shutdown(self):
        global flag_run

        if(not flag_run):        
            toast("shutting down system")
            if platform == "linux":    
                os.system("shutdown -h now")
            elif platform == "win":    
                os.system("shutdown /s /t 1")
        else:
            toast("cannot shutting down while measuring")

class ScreenData(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenData, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, DELAY_INITIAL)

    def delayed_init(self, dt):
        Clock.schedule_interval(self.regular_check_event, UPDATE_INTERVAL)

        self.ids.bt_shutdown.md_bg_color = "#A50000"
        layout = self.ids.layout_tables
        
        self.data_tables = MDDataTable(
            use_pagination=True,
            pagination_menu_pos="auto",
            rows_num=4,
            column_data=[
                ("No.", dp(10), self.sort_on_num),
                ("Volt [V]", dp(27)),
                ("Curr [mA]", dp(27)),
                ("Resi [kOhm]", dp(27)),
                ("Std Dev Res", dp(27)),
                ("IP (R decay)", dp(27)),
            ],
        )
        layout.add_widget(self.data_tables)

    def regular_check_event(self, dt):
        # print("this is regular check event at data screen")
        global flag_run, flag_run_prev
        global flag_measure
        global flag_dongle
        global count_mounting
        global dt_time
        global dt_cycle
        global dt_mode
        global inject_state
        global flag_autosave_data, flag_autosave_graph, graph_state
        global step, max_step
        global com_port_mcu

        screen_graph = self.screen_manager.get_screen('screen_graph')

        if flag_dongle:
            try:
                toast("Try mounting The Dongle")
                serial_file = os.path.join(DISK_ADDRESS, "serial.key")

                with open(serial_file,"r") as f:
                    serial_number = f.readline()
                    if serial_number == SERIAL_NUMBER:
                        toast("Successfully mounting The Dongle, the Serial number is valid")
                        self.ids.bt_save_data.disabled = False
                        screen_graph.ids.bt_save_graph.disabled = False
                        flag_dongle = False 
                    else:
                        toast("Failed mounting The Dongle, the Serial number is invalid")
                        self.ids.bt_save_data.disabled = True
                        screen_graph.ids.bt_save_graph.disabled = True
                        count_mounting += 1
                        if(count_mounting > DONGLE_MOUNT_MAX_RETRY):
                            flag_dongle = False                  
            except:
                toast("The Dongle could not be mounted")
                self.ids.bt_save_data.disabled = True
                screen_graph.ids.bt_save_graph.disabled = True
                count_mounting += 1
                if(count_mounting > DONGLE_MOUNT_MAX_RETRY):
                    flag_dongle = False 

        if(flag_run):
            self.ids.bt_measure.text = "STOP MEASUREMENT"
            self.ids.bt_measure.md_bg_color = "#A50000"

            screen_graph.ids.bt_measure.text = "STOP MEASUREMENT"
            screen_graph.ids.bt_measure.md_bg_color = "#A50000"
            flag_autosave_graph = True
            if(graph_state == 0):
                screen_graph.update_graph()

            flag_autosave_data = True
            measure_interval = (int(4 * dt_cycle * dt_time) / 1000)
            inject_interval = (int(dt_time) / 1000)

            if("(VES) VERTICAL ELECTRICAL SOUNDING" in dt_mode):
                if(flag_measure == False):
                    Clock.schedule_interval(self.measurement_check_event, measure_interval)
                    Clock.schedule_interval(self.inject_current_event, inject_interval)
                flag_measure = True
        
            elif("(SP) SELF POTENTIAL" in dt_mode):
                if(flag_measure == False):
                    Clock.schedule_interval(self.measurement_check_event, measure_interval)
                    Clock.schedule_interval(self.measurement_sampling_event, inject_interval)
                flag_measure = True
                
            elif("(R) RESISTIVITY" in dt_mode):
                if(flag_measure == False):
                    Clock.schedule_interval(self.measurement_check_event, measure_interval)
                    Clock.schedule_interval(self.inject_current_event, inject_interval)
                flag_measure = True
                
            elif("(R+IP) INDUCED POLARIZATION" in dt_mode):
                if(flag_measure == False):
                    Clock.schedule_interval(self.measurement_check_event, measure_interval)
                    Clock.schedule_interval(self.inject_current_event, inject_interval)
                flag_measure = True                        
            else:
                pass

        else:
            self.ids.bt_measure.text = "RUN MEASUREMENT"
            self.ids.bt_measure.md_bg_color = "#196BA5"
            self.stop_measure()

            screen_graph.ids.bt_measure.text = "RUN MEASUREMENT"
            screen_graph.ids.bt_measure.md_bg_color = "#196BA5"
            if(flag_autosave_graph):
                screen_graph.autosave_graph()
                flag_autosave_graph = False

        if(flag_run == False and flag_run_prev == True):
            self.reset_switching()
        
        flag_run_prev = flag_run
        graph_state += 1

    def stop_measure(self):
        global flag_measure
        global inject_state
        global flag_autosave_data
        global step
        global max_step
        global com_port_mcu

        self.ids.bt_measure.text = "RUN MEASUREMENT"
        self.ids.bt_measure.md_bg_color = "#196BA5"
        Clock.unschedule(self.measurement_sampling_event)
        Clock.unschedule(self.measurement_check_event)
        Clock.unschedule(self.inject_current_event)
        inject_state = 0
        flag_measure = False
        step = 0
        max_step = 0

        if flag_autosave_data:
            self.autosave_data()
            flag_autosave_data = False

    def measurement_check_event(self, dt):
        # print("this is measurement check event at data screen")
        global flag_run
        global dt_time, dt_cycle
        global data_base
        global arr_electrode, data_electrode
        global dt_current, dt_voltage
        global x_electrode
        global step
        global com_port_mcu

        if("WENNER (ALPHA)" in dt_config):
            k = 2 * np.pi * dt_distance * dt_constant
        elif("WENNER (BETA)" in dt_config):
            k = 6 * np.pi * dt_distance * dt_constant
        elif("WENNER (GAMMA)" in dt_config):
            k = 3 * np.pi * dt_distance * dt_constant
        elif("POLE-POLE" in dt_config):
            k = 2 * np.pi * dt_distance * dt_constant
        elif("DIPOLE-DIPOLE" in dt_config):
            k = np.pi * dt_distance * dt_constant * (dt_constant + 1) * (dt_constant + 2)
        elif("SCHLUMBERGER" in dt_config):
            k = np.pi * dt_distance * dt_constant * (dt_constant + 1)
        else:
            k = 1

        voltage = np.max(np.fabs(dt_voltage))
        current = np.max(np.fabs(dt_current))
        if(current > 0.0):
            resistivity = k * voltage / current
            resistivity = k * voltage / current
        else:
            resistivity = 0.0
            resistivity = 0.0
            
        std_resistivity = np.std(data_base[2, :])
        ip_decay = (np.sum(dt_voltage) / voltage ) * (int(dt_cycle * dt_time)/10000)

        data_acquisition = np.array([voltage, current, resistivity, std_resistivity, ip_decay])
        data_acquisition.resize([5, 1])
        data_base = np.concatenate([data_base, data_acquisition], axis=1)

        try:
            data_c1 = arr_electrode[0, step] + 1
            data_p1 = arr_electrode[1, step] + 1
            data_p2 = arr_electrode[2, step] + 1
            data_c2 = arr_electrode[3, step] + 1
            electrode_pos = np.array([data_c1, data_p1, data_p2, data_c2])
        except:
            electrode_pos = np.array([1, 2, 3, 4])

        electrode_pos.resize([4, 1])
        data_electrode = np.concatenate([data_electrode, electrode_pos], axis=1)

        self.ids.realtime_voltage.text = f"{voltage:.3f}"
        self.ids.realtime_current.text = f"{current:.3f}"
        self.ids.realtime_resistivity.text = f"{resistivity:.3f}"

        avg_voltage = np.average(data_base[0, :])
        avg_current = np.average(data_base[1, :])
        avg_resistivity = np.average(data_base[2, :])

        self.ids.average_voltage.text = f"{avg_voltage:.3f}"
        self.ids.average_current.text = f"{avg_current:.3f}"
        self.ids.average_resistivity.text = f"{avg_resistivity:.3f}"

        avg_voltage = np.average(data_base[0, :])
        avg_current = np.average(data_base[1, :])
        avg_resistivity = np.average(data_base[2, :])

        self.ids.average_voltage.text = f"{avg_voltage:.3f}"
        self.ids.average_current.text = f"{avg_current:.3f}"
        self.ids.average_resistivity.text = f"{avg_resistivity:.3f}"

        self.data_tables.row_data=[(f"{i + 1}", f"{data_base[0,i]:.3f}", f"{data_base[1,i]:.3f}", f"{data_base[2,i]:.3f}", f"{data_base[3,i]:.3f}", f"{data_base[4,i]:.3f}") for i in range(len(data_base[1]))]

    def inject_current_event(self, dt):
        # print("this is inject current event at data screen")
        global inject_state, step
        global dt_cycle, dt_time
        global com_port_mcu

        time_sampling = (int(dt_time) / 10000)
        # print("sampling time:", time_sampling, ", inject state:", inject_state)
        if(inject_state >= int(4 * dt_cycle)):
            Clock.unschedule(self.measurement_sampling_event)
            inject_state = 0
            step += 1

        Logger.info("sampling time: %s, inject state: %s", time_sampling, inject_state)

        if inject_state in {0, 4, 8, 12, 16, 20, 24, 28, 32, 36}:
            # Clock.unschedule(self.measurement_sampling_event)
            toast_msg = "Measurement " + str(step + 1)
            toast(toast_msg)
            if(not DEBUG):
                com_port_mcu.write(b".") # inject positive current
                data_stop_inject = com_port_mcu.readline().decode("utf-8").strip()
                print(data_stop_inject)
                # toast(data_stop_inject)
                while True:  
                    if data_stop_inject == "Not Injected":
                        break
                    else:
                        com_port_mcu.write(b".")
                        data_stop_inject = com_port_mcu.readline().decode("utf-8").strip()
                self.switching_commands()
            
        elif inject_state in {1, 5, 9, 13, 17, 21, 25, 29, 33, 37}:            # Clock.schedule_interval(self.measurement_sampling_event, time_sampling)
            if(not DEBUG):
                com_port_mcu.write(b"+")
                data_plus_inject = com_port_mcu.readline().decode("utf-8").strip()
                print(data_plus_inject)
                # toast(data_plus_inject)
                while True:
                    if data_plus_inject == "Inject Positif":
                        break
                    else:
                        com_port_mcu.write(b"+")
                        data_plus_inject = com_port_mcu.readline().decode("utf-8").strip()

                data_indikasi_lanjut = com_port_mcu.readline().decode("utf-8").strip()
                print(data_indikasi_lanjut)
                # toast(data_indikasi_lanjut)
                while True:
                    if data_indikasi_lanjut == "Silahkan":
                        self.measurement_sampling_event(time_sampling)
                        break
                    else:
                        data_indikasi_lanjut = com_port_mcu.readline().decode("utf-8").strip()
            
        elif inject_state in {2, 6, 10, 14, 18, 22, 26, 30, 34, 38}:
        # Clock.unschedule(self.measurement_sampling_event)
            if(not DEBUG):
                com_port_mcu.write(b".")
                data_stop_inject = com_port_mcu.readline().decode("utf-8").strip()
                print(data_stop_inject)
                # toast(data_stop_inject)
                while True:
                    if data_stop_inject == "Not Injected":
                        break
                    else:
                        com_port_mcu.write(b".")
                        data_stop_inject = com_port_mcu.readline().decode("utf-8").strip()
            
        elif inject_state in {3, 7, 11, 15, 19, 23, 27, 31, 35, 39}:            
            Clock.schedule_interval(self.measurement_sampling_event, time_sampling)
            if(not DEBUG):
                com_port_mcu.write(b"-")
                data_negatif_inject = com_port_mcu.readline().decode("utf-8").strip()
                print(data_negatif_inject)
                # toast(data_negatif_inject)
                while True:
                    if data_negatif_inject == "Inject Negatif":
                        break
                    else:
                        com_port_mcu.write(b"-")
                        data_negatif_inject = com_port_mcu.readline().decode("utf-8").strip()

                data_indikasi_lanjut = com_port_mcu.readline().decode("utf-8").strip()
                print(data_indikasi_lanjut)
                # toast(data_indikasi_lanjut)
                while True:
                    if data_indikasi_lanjut == "Silahkan":
                        self.measurement_sampling_event(time_sampling)
                        break
                    else:
                        data_indikasi_lanjut = com_port_mcu.readline().decode("utf-8").strip()

        inject_state += 1
        
    def measurement_sampling_event(self, dt):
        # print("this is measurment sampling event at data screen")
        global dt_current, dt_voltage
        global com_port_mcu
        global flag_run

        # Data acquisition
        dt_voltage_temp = np.zeros_like(dt_voltage)
        dt_current_temp = np.zeros_like(dt_current)

        if(flag_run):
            if (not DEBUG):
                #try:
                com_port_mcu.write(b"a")
                data_current = com_port_mcu.readline().decode("utf-8").strip()  # read the incoming data and remove newline character
                while True:
                    if data_current[0] == "a":
                        curr = float(data_current[1:])
                        realtime_current = curr
                        
                        print("Realtime Curr:", realtime_current)
                        dt_current_temp[:1] = realtime_current
                        #time.sleep(0.5)
                        break
                    else:
                        com_port_mcu.write(b"a")
                        data_current = com_port_mcu.readline().decode("utf-8").strip()  # read the incoming data and remove newline character
                #except:
                    #toast("Error read Current")
                    #dt_current_temp[:1] = 0.0
                
                #try:
                com_port_mcu.write(b"v")
                data_millivoltage = com_port_mcu.readline().decode("utf-8").strip()  # read the incoming data and remove newline character
                #print(data_millivoltage)
                while True:
                    if data_millivoltage[0] == 'v':
                        millivolt = float(data_millivoltage[1:])
                        volt = millivolt / 1000
                        realtime_voltage = volt

                        print("Realtime Volt:", realtime_voltage)
                        dt_voltage_temp[:1] = realtime_voltage
                        #print(data_millivoltage)
                        break
                    else:
                        com_port_mcu.write(b"v")
                        data_millivoltage = com_port_mcu.readline().decode("utf-8").strip()
                #except:
                #   toast("Error read Voltage")
                #  dt_voltage_temp[:1] = 0.0

        dt_voltage_temp[1:] = dt_voltage[:-1]
        dt_voltage = dt_voltage_temp

        dt_current_temp[1:] = dt_current[:-1]
        dt_current = dt_current_temp


    def switching_commands(self):
        global step
        global max_step

        try:
            reshaped_data_rtu = data_rtu.T[step,:].reshape(6, 36)

            data_rtu1 = reshaped_data_rtu[0]
            data_rtu2 = reshaped_data_rtu[1]
            data_rtu3 = reshaped_data_rtu[2]
            data_rtu4 = reshaped_data_rtu[3]
            data_rtu5 = reshaped_data_rtu[4]
            data_rtu6 = reshaped_data_rtu[5]

            rtu1.write_bits(80, data_rtu1.tolist()) 
            rtu2.write_bits(80, data_rtu2.tolist()) 
            rtu3.write_bits(80, data_rtu3.tolist()) 
            rtu4.write_bits(80, data_rtu4.tolist()) 
            rtu5.write_bits(80, data_rtu5.tolist()) 
            rtu6.write_bits(80, data_rtu6.tolist()) 
        except:
            pass

    def reset_switching(self):
        try:
            data_rtu1 = np.zeros(36, dtype=int)
            data_rtu2 = np.zeros(36, dtype=int)
            data_rtu3 = np.zeros(36, dtype=int)
            data_rtu4 = np.zeros(36, dtype=int)
            data_rtu5 = np.zeros(36, dtype=int)
            data_rtu6 = np.zeros(36, dtype=int)

            rtu1.write_bits(80, data_rtu1.tolist()) 
            rtu2.write_bits(80, data_rtu2.tolist()) 
            rtu3.write_bits(80, data_rtu3.tolist()) 
            rtu4.write_bits(80, data_rtu4.tolist()) 
            rtu5.write_bits(80, data_rtu5.tolist()) 
            rtu6.write_bits(80, data_rtu6.tolist()) 
        except:
            pass

    # def switching_commands(self):
    #     global step
    #     global max_step
    #     global com_port_mcu
    #     global arr_electrode

    #     try:
    #         serial_text = str(f"*{arr_electrode[0, step]},{arr_electrode[1, step]},{arr_electrode[2, step]},{arr_electrode[3, step]}")
    #         print(serial_text)
    #         com_port_mcu.write(serial_text.encode('utf-8'))
    #         validasi_patok = com_port_mcu.readline()#.decode("utf-8").strip()
    #         while True:
    #             print(validasi_patok)
    #             if  validasi_patok == 'Good':
    #                 break
    #             else :
    #                 com_port_mcu.write(serial_text.encode('utf-8'))
    #                 print(serial_text)
    #                 #time.sleep(0.1)
    #                 validasi_patok = com_port_mcu.readline().decode("utf-8").strip()
    #                 print(validasi_patok)
    #     except:
    #         pass
                   

    # def reset_switching(self):
    #     try:
    #         com_port_mcu.write(b"%") # reset switching
    #         data_reset = com_port_mcu.readline().decode("utf-8").strip()  # read the incoming data and remove newline character
    #         while True:
    #             print(data_reset)
    #             if data_reset == "Semua decoder mati":
    #                 break
    #             else:
    #                 com_port_mcu.write(b"%") # reset switching
    #                 data_reset = com_port_mcu.readline().decode("utf-8").strip()
            
    #         com_port_mcu.write(b"_")
    #         data_stop_inject = com_port_mcu.readline().decode("utf-8").strip()
    #         while True:
    #             print(data_stop_inject)
    #             if data_stop_inject == "Not Injected":
    #                 break
    #             else:
    #                 com_port_mcu.write(b"_")
    #                 data_stop_inject = com_port_mcu.readline().decode("utf-8").strip()
    #     except:
    #         print("Error reset switching")

    def reset_data(self):
        global data_base
        global data_electrode
        global dt_measure
        global dt_current
        global dt_voltage
        global flag_run
        global com_port_mcu

        if(not flag_run):
            try:
                toast("Resetting data")
                data_base = np.zeros([5, 0])
                data_electrode = np.zeros([4, 0], dtype=int)
                dt_measure = np.zeros(6)
                dt_current = np.zeros(10)
                dt_voltage = np.zeros(10)
                
                layout = self.ids.layout_tables
                
                self.data_tables = MDDataTable(
                    use_pagination=True,
                    pagination_menu_pos="auto",
                    rows_num=4,
                    column_data=[
                        ("No.", dp(10), self.sort_on_num),
                        ("Volt [V]", dp(27)),
                        ("Curr [mA]", dp(27)),
                        ("Resi [kOhm]", dp(27)),
                        ("Std Dev Res", dp(27)),
                        ("IP (R decay)", dp(27)),
                    ],
                )
                layout.add_widget(self.data_tables)
                toast("Successfully reset data")
            except Exception as e:
                print(f"Error reset data: {e}")
                toast("Error reset data")
        else:
            toast("Cannot reset data while measuring")
        

    def sort_on_num(self, data):
        try:
            return zip(
                *sorted(
                    enumerate(data),
                    key=lambda l: l[0][0]
                )
            )
        except:
            toast("Error sorting data")
            
    def save_data(self):
        global data_base, data_electrode
        global dt_distance, dt_config
        global data_pos
        global com_port_mcu

        if(not flag_run):
            if("WENNER (ALPHA)" in dt_config):
                mode = 1
            elif("WENNER (BETA)" in dt_config):
                mode = 1
            elif("WENNER (GAMMA)" in dt_config):
                mode = 1
            elif("POLE-POLE" in dt_config):
                mode = 2
            elif("DIPOLE-DIPOLE" in dt_config):
                mode = 3
            elif("SCHLUMBERGER" in dt_config):
                mode = 7
            toast("Saving data")

            try:
                data = data_base[2, :]
                x_loc = data_pos[0, :data.size]
                spaces = np.ones_like(data) * dt_distance
                data_write = np.vstack((x_loc, spaces, data))
                # data_write = np.vstack((data_write, data))
                if(data_write.size == 0):
                    data_write = np.array([[0,1,2,3]])
                print(data_write)
            except Exception as e:
                toast("Error saving data, measurement is not completed yet")

            now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S.dat")                
            head="%s \n%.2f \n%s \n%s \n0 \n1" % (now, dt_distance, mode, data.size)
            foot="0 \n0 \n0 \n0 \n0"
            try:
                path_name = os.path.join(DISK_ADDRESS, "data")
                file_name = os.path.join(path_name, now)

                if(not os.path.isdir(path_name)):
                    os.mkdir(path_name)

                with open(file_name,"wb") as f:
                    np.savetxt(f, data_write.T, fmt="%.3f", delimiter="\t", header=head, footer=foot, comments="")
                print("Sucessfully save data to The Dongle")
                toast("Sucessfully save data to The Dongle")
            except:
                try:
                    path_name = os.path.join(os.getcwd(), "data")
                    file_name = os.path.join(path_name, now)

                    if(not os.path.isdir(path_name)):
                        os.mkdir(path_name)

                    with open(file_name,"wb") as f:
                        np.savetxt(f, data_write.T, fmt="%.3f", delimiter="\t", header=head, footer=foot, comments="")
                    print("sucessfully save data to The Default Directory")
                    toast("Sucessfully save data to The Default Directory")
                except Exception as e:
                    print("Error save data " + str(e))
                    # toast("Error saving data")
        else:
            toast("Cannot save data while measuring")

    def autosave_data(self):
        global data_base, data_electrode

        data_save = np.vstack((data_electrode, data_base))
        now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S.raw")
        try:
            path_name = os.path.join(DISK_ADDRESS, "data")
            file_name = os.path.join(path_name, now)

            if(not os.path.isdir(path_name)):
                os.mkdir(path_name)

            with open(file_name,"wb") as f:
                np.savetxt(f, data_save.T, fmt="%.3f",delimiter="\t",header="C1  \t P1  \t P2  \t C2  \t Volt [V] \t Curr [mA] \t Res [kOhm] \t StdDev \t IP [R decay]")
            # print("sucessfully auto save data to Dongle")
            toast("Sucessfully auto save data to The Dongle")
        except:
            try:
                path_name = os.path.join(os.getcwd(), "data")
                file_name = os.path.join(path_name, now)

                if(not os.path.isdir(path_name)):
                    os.mkdir(path_name)

                with open(file_name,"wb") as f:
                    np.savetxt(f, data_save.T, fmt="%.3f",delimiter="\t",header="C1  \t P1  \t P2  \t C2  \t Volt [V] \t Curr [mA] \t Res [kOhm] \t StdDev \t IP [R decay]")
                # print("sucessfully auto save data to Default Directory")
                toast("Sucessfully save data to The Default Directory")
            except Exception as e:
                print("Error autosave data" + str(e))
                # toast("Error auto saving data")

    def measure(self):
        global flag_run
        global com_port_mcu
        if(flag_run):
            flag_run = False
        else:
            flag_run = True

    def screen_setting(self):
        self.screen_manager.current = 'screen_setting'

    def screen_data(self):
        self.screen_manager.current = 'screen_data'

    def screen_graph(self):
        self.screen_manager.current = 'screen_graph'

    def exec_shutdown(self):
        global flag_run

        if(not flag_run):        
            toast("Shutting down system")
            if platform == "linux":    
                os.system("shutdown -h now")
            elif platform == "win":    
                os.system("shutdown /s /t 1")
        else:
            toast("Cannot shutting down while measuring") 

class ScreenGraph(MDScreen):
    def __init__(self, **kwargs):
        super(ScreenGraph, self).__init__(**kwargs)
        Clock.schedule_once(self.delayed_init, DELAY_INITIAL)

    def delayed_init(self, dt):
        Clock.schedule_interval(self.regular_check_event, UPDATE_INTERVAL_GRAPH)

        self.ids.bt_shutdown.md_bg_color = "#A50000"
        self.fig, self.ax = plt.subplots()
        self.fig.set_facecolor("#eeeeee")
        self.fig.tight_layout()
        l, b, w, h = self.ax.get_position().bounds
        self.ax.set_position(pos=[l, b + 0.3*h, w, h*0.7])
        
        self.ax.set_xlabel("distance [m]", fontsize=10)
        self.ax.set_ylabel("n", fontsize=10)

        self.ids.layout_graph.add_widget(FigureCanvasKivyAgg(self.fig))        

    def regular_check_event(self, dt):
        # print("this is regular check event at graph screen")
        global flag_run
        global flag_dongle
        global count_mounting
        global dt_time
        global data_base
        global flag_autosave_graph
        global graph_state
        global com_port_mcu

        if(graph_state > GRAPH_STATE_COUNT):
            graph_state = 0

    def update_graph(self):
        global flag_run
        global x_datum
        global y_datum
        global data_base
        global data_pos

        data_limit = len(data_base[2,:])
        visualized_data_pos = data_pos

        try:
            self.fig.set_facecolor("#eeeeee")
            self.fig.tight_layout()
            
            self.ax.set_xlabel("distance [m]", fontsize=10)
            self.ax.set_ylabel("n", fontsize=10)
            self.ax.set_facecolor("#eeeeee")

            # datum location
            max_data = np.max(data_base[2,:data_limit])
            cmap, norm = mcolors.from_levels_and_colors([-max_data - 10, 0.0, max_data + 10],['green','red'])
            self.ax.scatter(visualized_data_pos[0,:data_limit], -visualized_data_pos[1,:data_limit], c=data_base[2,:data_limit], cmap=cmap, norm=norm, label=l_electrode[0], marker='o')
            
            # electrode location
            self.ids.layout_graph.clear_widgets()
            self.ids.layout_graph.add_widget(FigureCanvasKivyAgg(self.fig))

            # print("successfully show graphic")
            toast("Successfully show graphic")
        
        except:
            print("Error show graphic")
            # toast("error show graphic")

        if(data_limit >= len(data_pos[0,:])):
            self.measure()

    def measure(self):
        global flag_run
        if(flag_run):
            flag_run = False
        else:
            flag_run = True

    def reset_graph(self):
        global data_base
        global data_pos
        global flag_run

        if(not flag_run):        
            toast("Resetting graph")
            data_base = np.zeros([5, 0])
            data_pos = np.zeros([2, 0])

            try:
                self.ids.layout_graph.remove_widget(FigureCanvasKivyAgg(self.fig))
                self.fig, self.ax = plt.subplots()
                self.fig.set_facecolor("#eeeeee")
                self.fig.tight_layout()
                l, b, w, h = self.ax.get_position().bounds
                self.ax.set_position(pos=[l, b + 0.3*h, w, h*0.7])
                
                self.ax.set_xlabel("distance [m]", fontsize=10)
                self.ax.set_ylabel("n", fontsize=10)
                self.ids.layout_graph.clear_widgets()
                self.ids.layout_graph.add_widget(FigureCanvasKivyAgg(self.fig))        
                # print("successfully reset graph")
                toast("Successfully reset graph")
            
            except Exception as e:
                print(f"error reset graph: {e}")
                toast("Error reset graph")
        else:
            toast("Cannot reset graph while measuring")


    def save_graph(self):
        if(not flag_run):        
            toast("Saving graph")
            now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S.jpg")
            try:
                path_name = os.path.join(DISK_ADDRESS, "graph")
                file_name = os.path.join(path_name, now)

                if(not os.path.isdir(path_name)):
                    os.mkdir(path_name)

                self.fig.savefig(file_name)
                # print("sucessfully save graph to Dongle")
                toast("Sucessfully save graph to The Dongle")
            except:
                try:
                    path_name = os.path.join(os.getcwd(), "graph")
                    file_name = os.path.join(path_name, now)

                    if(not os.path.isdir(path_name)):
                        os.mkdir(path_name)
                        
                    self.fig.savefig(file_name)
                    # print("sucessfully save graph to Default Directory")
                    toast("Sucessfully save graph to The Default Directory")
                except Exception as e:
                    print(f"Error saving graph: {e}")
                    # toast("Error saving graph")
        else:
            toast("Cannot save graph while measuring")

    def autosave_graph(self):
        now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S.jpg")
        try:           
            path_name = os.path.join(DISK_ADDRESS, "graph")
            file_name = os.path.join(path_name, now)

            if(not os.path.isdir(path_name)):
                os.mkdir(path_name)

            self.fig.savefig(file_name)
            # print("sucessfully auto save graph to Dongle")
            toast("Sucessfully auto save graph to The Dongle")
        except:
            try:
                path_name = os.path.join(os.getcwd(), "graph")
                file_name = os.path.join(path_name, now)

                if(not os.path.isdir(path_name)):
                    os.mkdir(path_name)

                self.fig.savefig(file_name)
                # print("sucessfully auto save graph to Default Directory")
                toast("Sucessfully auto save graph to The Default Directory")
            except Exception as e:
                print(f"Error auto saving graph {e}")
                # toast("Error auto saving graph")
                
    def screen_setting(self):
        self.screen_manager.current = 'screen_setting'

    def screen_data(self):
        self.screen_manager.current = 'screen_data'

    def screen_graph(self):
        self.screen_manager.current = 'screen_graph'

    def exec_shutdown(self):
        global flag_run

        if(not flag_run):        
            toast("Shutting down system")
            if platform == "linux":    
                os.system("shutdown -h now")
            elif platform == "win":    
                os.system("shutdown /s /t 1")
        else:
            toast("Cannot shutting down while measuring")

class RootScreen(ScreenManager):
    pass  

class ResistivityMeterApp(MDApp):
    def build(self):
        self.theme_cls.colors = colors
        self.theme_cls.primary_palette = "Blue"
        self.icon = 'asset/logo_labtek_p.png'
        Window.fullscreen = 'auto'
        Window.borderless = True
        # Window.size = 1024, 600
        Window.allow_screensaver = True

        Builder.load_file('main.kv')
        return RootScreen()

if __name__ == '__main__':
    ResistivityMeterApp().run()