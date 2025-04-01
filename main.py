from infi.systray import SysTrayIcon
from onkyo import AVRControl as av
from onkyo import time

ip_address = "192.168.1.150"
monitor_model = "S3220DGF"

main = av(ip_address,monitor_model)

def reconnect(systray):
    main.disconnect_receiver()
    main.noti("AVR Disconnected")
    time.sleep(2)
    try:
        main.connect_receiver(ip_address)
    except Exception as e:
        main.noti(f"Error: {e}")
    index = main.get_monitor_index()
    main.set_monitor_index(index)

def exit_app(systray):
    main.stop()

menu_options = (("Reconnect",None, reconnect),)
systray = SysTrayIcon("icon.ico","AVR Control", menu_options, on_quit=exit_app) 

if __name__ == "__main__":
    systray.start()
    main.run()
    
