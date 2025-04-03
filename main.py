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
    main.disconnect_receiver()
    main.noti("AVR Disconnected")
    time.sleep(2)
    try:
        main.connect_receiver(ip_address)
    except Exception as e:
        main.noti(f"Error: {e}")
    main.get_main_monitor()

def exit_app(systray):
    main.stop()

menu_options = (("Reconnect",None, reconnect),)
systray = SysTrayIcon("icon.ico","AVR Control", menu_options, on_quit=exit_app) 

if __name__ == "__main__":
    systray.start()
    main.run()
    
