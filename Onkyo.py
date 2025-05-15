import keyboard
import eiscp
import time
from notifypy import Notify
from monitorcontrol import get_monitors
from ping3 import ping

class AVRControl:
    def __init__(self,ip_address,model,amount):
        self.ip_address= ip_address   
        self.receiver = None                              #Zone 2 has to stay on to establish connection in standby mode
        self.sourceBD = "SLI10"
        self.sourcePC= "SLI05"
        self.sourceGame = "SLI02"
        self.zoneBD = "SLZ10"
        self.zoneGame = "SLZ02"
        self.powerOn = "PWR01"
        self.powerOff = "PWR00"
        self.volumeUP = "MVLUP"
        self.volumeDOWN= "MVLDOWN"
        self.hdmiAudioOn= "HAO01"
        self.hdmiAudioOff= "HAO00"
        self.monitorDP = 15
        self.monitorHDMI= 17
        self.monitorHDMI2= 18
        self.running= True
        self.monitors = None 
        self.monitor_model = model
        self.monitor_amount = amount
        self.last_message = None

    def get_main_monitor(self):    
        for x in range(self.monitor_amount):   
            try:
                self.monitors = get_monitors()[x]   
                with self.monitors:
                    test = self.monitors.get_vcp_capabilities()
                    if test["model"] == self.monitor_model:
                        break
            except Exception:
                pass
             
        
    def noti(self,message_user:str):
        if self.last_message == message_user:
            return
        self.last_message = message_user
        notification = Notify()
        notification.title = "Onkyo Control"
        notification.timeout = 1000
        notification.message = self.last_message
        notification.icon = "icon.ico"
        notification.send()

    def connect_receiver(self,ip_address):
        try:
            self.receiver = eiscp.eISCP(ip_address)
            if self.test_onkyo():
                self.noti("AVR Connected")
        except Exception as e:
            self.noti(f"Error: {e}")
    
    def disconnect_receiver(self):
        self.receiver.disconnect()

    def default_startup(self):
        try:
            self.receiver.raw(self.powerOn)  
            self.receiver.raw(self.sourcePC)
            with self.monitors as monitor:
                if (monitor.get_input_source() != "InputSource.DP1"):
                    monitor.set_input_source(self.monitorDP)
            self.noti("Switched On")
            self.receiver.raw(self.hdmiAudioOff)
        except Exception as e:
            self.noti(f"Error switching on: {e}")
    
    def toggle_power(self): #switch AVR on and off
        power_state = self.receiver.raw("PWRQSTN")
        try:
            if power_state == self.powerOn:
                self.receiver.raw(self.powerOff)  # Turn off
                self.noti("Power: OFF")
                power_state = self.receiver.raw("PWRQSTN")

            else:
                self.receiver.raw(self.powerOn)  # Turn on
                self.noti("Power: ON")
                power_state = self.receiver.raw("PWRQSTN")

            time.sleep(1)
        except Exception as e:
                self.noti(f"Error toggling power: {e}")

    def change_source(self,source,input,message):  #change HDMI Input
        self.get_main_monitor()
        try:
            self.receiver.raw(self.hdmiAudioOff)  
            self.receiver.raw(source)  
            self.noti(message)
            with self.monitors as monitor:
                monitor.set_input_source(input)
        except Exception as e:
                self.noti(f"Error toggling Source: {e}")

    def change_zone(self,zone,message): #Change Zone2 Input
        try:
            self.receiver.raw(zone) 
            self.noti(message)
            time.sleep(1)
        except Exception as e:
            self.noti(f"Error switching to Source: {e}")

    def change_HDMI_audio(self): #Switch HDMI Out Audio on and off
        global hdmiAudio_state
        hdmiAudio_state= self.receiver.raw("HAOQSTN")
        try:
            if hdmiAudio_state == self.hdmiAudioOn:
                self.receiver.raw(self.hdmiAudioOff)  
                self.noti("HDMI Audio: OFF")
                hdmiAudio_state= self.receiver.raw("HAOQSTN")
            else:
                self.receiver.raw(self.hdmiAudioOn)  # Turn on
                self.noti("HDMI Audio: ON")
                hdmiAudio_state= self.receiver.raw("HAOQSTN")
            time.sleep(1)
        except Exception as e:
                self.noti(f"Error toggling power: {e}")

    def change_volume(self,change): #change main volume
        try:
            self.receiver.raw(change) 
        except Exception as e:
            self.noti(f"Error changing Volume: {e}")
        
    def setup_hotkeys(self):
        keyboard.add_hotkey('ctrl+alt+p', self.toggle_power)
        keyboard.add_hotkey('ctrl+alt+F1', lambda: self.change_source(self.sourcePC,self.monitorDP, "Source: PC"))
        keyboard.add_hotkey('ctrl+alt+F2', lambda: self.change_source(self.sourceBD,self.monitorHDMI2, "Source: BD"))
        keyboard.add_hotkey('ctrl+alt+F3', lambda: self.change_source(self.sourceGame,self.monitorHDMI, "Source: Game"))
        #keyboard.add_hotkey('ctrl+alt+F6', lambda: self.change_zone(self.zoneDefault,"Zone 2: PC")) not using Zone 2 anymore
        keyboard.add_hotkey('ctrl+alt+F5', self.change_HDMI_audio)
        keyboard.add_hotkey('ctrl+alt+up', lambda: self.change_volume(self.volumeUP))
        keyboard.add_hotkey('ctrl+alt+down', lambda: self.change_volume(self.volumeDOWN))
        keyboard.add_hotkey('ctrl+alt+R', self.reconnect)
    
    def run(self):
        self.connect_receiver(self.ip_address)
        self.get_main_monitor()
        self.default_startup()
        self.setup_hotkeys()

        while self.running:
            time.sleep(10)
            self.test_onkyo()

    def reconnect(self):
        self.disconnect_receiver()
        self.connect_receiver(self.ip_address)

    def stop(self):
        self.running=False
        self.disconnect_receiver()

    def test_onkyo(self):
        response = ping(self.ip_address, 2)
        if response is not None:
            return True
        else:
            self.noti(f"Cant Reach AVR: Retry Connection")
            self.reconnect()

 

        