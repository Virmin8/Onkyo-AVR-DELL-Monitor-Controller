from infi.systray import SysTrayIcon
from onkyo import AVRControl as av
from onkyo import time
import yaml
import threading

with open('config.yaml') as config:
    config_dict = yaml.safe_load(config)

ip_address = config_dict['ip_address']
monitor_model = config_dict['monitor_model']
default_input = config_dict['default_input']


main = av(ip_address,monitor_model,default_input)

def reconnect(systray):
    main.reconnect()
    
def exit_app(systray):
    main.stop()

menu_options = (("Reconnect",None, reconnect),)
systray = SysTrayIcon("icon.ico","AVR Control", menu_options, on_quit=exit_app) 

if __name__ == "__main__":
    threading.Thread(target=main.run, daemon=True).start()
    systray.start()