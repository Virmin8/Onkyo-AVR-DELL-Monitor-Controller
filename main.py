import pystray
from PIL import Image
import threading
from onkyo import AVRControl as av
from onkyo import time
import os

ip_address = "192.168.1.150"
image = Image.open("icon.png")

def after_click(icon, query):
    if str(query) == "Reload":
        main.disconnect_receiver()
        main.noti("Disconnected")
        time.sleep(5)
        try:
            main.connect_receiver(ip_address)
            main.noti("Connected")
        except Exception as e:
            main.noti(f"Error: {e}")

    elif str(query) == "Exit":
        main.exit()
        icon.stop()
        os._exit(0) 
        
 

icon = pystray.Icon("AVR", image, "AVR Control", 
                    menu=pystray.Menu(
    pystray.MenuItem("Reconnect", 
                     after_click),
    pystray.MenuItem("Exit", after_click)))
 
if __name__ == "__main__":
    threading.Thread(daemon=True, target=icon.run).start()
    main = av(ip_address)
    main.run()
    
