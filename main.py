from infi.systray import SysTrayIcon
from onkyo import AVRControl as av
from onkyo import time
import yaml

with open('config.yaml') as config:
    config_dict = yaml.safe_load(config)

ip_address = config_dict['ip_address']
monitor_model = config_dict['monitor_model']
monitor_amount = config_dict['monitor_amount']

main = av(ip_address,monitor_model,monitor_amount)

def reconnect(systray):
    main.stop()
    main.run()
    
def exit_app(systray):
    main.stop()

menu_options = (("Reconnect",None, reconnect),)
systray = SysTrayIcon("icon.ico","AVR Control", menu_options, on_quit=exit_app) 


if __name__ == "__main__":
    systray.start()
    main.run()
    
