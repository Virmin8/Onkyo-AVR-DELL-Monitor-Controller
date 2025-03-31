from infi.systray import SysTrayIcon
from onkyo import AVRControl as av
from onkyo import time

ip_address = "192.168.1.150"
main = av(ip_address)

def reconnect(systray):
    main.disconnect_receiver()
    main.noti("Disconnected")
    time.sleep(2)
    try:
        main.connect_receiver(ip_address)
        main.noti("Connected")
    except Exception as e:
        main.noti(f"Error: {e}")

def exit_app(systray):
    main.stop()

menu_options = (("Reconnect",None, reconnect),)
systray = SysTrayIcon("icon.ico","AVR Control", menu_options, on_quit=exit_app) 

if __name__ == "__main__":
    systray.start()
    main.run()
    
