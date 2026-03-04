import keyboard
import eiscp
import time
from notifypy import Notify
from monitorcontrol import *
from ping3 import ping
import threading
from Volume import VolumeOSD

class AVRControl:
    def __init__(self,ip_address,model,default_input):
        self.ip_address = ip_address
        self.receiver = None
        self.monitor = None
        self.monitor_model = model

        # AVR Commands
        self.sourceBD = "SLI10"
        self.sourcePC = "SLI05"
        self.sourceGame = "SLI02"
        self.zoneBD = "SLZ10"
        self.zoneGame = "SLZ02"
        self.powerOn = "PWR01"
        self.powerOff = "PWR00"
        self.volumeUP = "MVLUP"
        self.volumeDOWN = "MVLDOWN"
        self.hdmiAudioOn = "HAO01"
        self.hdmiAudioOff = "HAO00"

        # Monitor Inputs
        self.monitorDP = "DP1"
        self.monitorHDMI = "HDMI1"
        self.monitorHDMI2 = "HDMI2"
        self.defaultInput = default_input

        # State
        self.running = True
        self.last_message = None
        self.hdmiAudio_state = None

        self.current_volume = None
        

    def get_main_monitor(self):    
        for monitor in get_monitors():
            try:
                with monitor:
                    x = monitor.get_vcp_capabilities()
                    print (x)
                    if x["model"] == self.monitor_model:
                        self.monitors = monitor
                        break
            except Exception:
                pass
             
        
    def noti(self,message_user:str):
        if self.last_message == message_user:
            return
        self.last_message = message_user
        notification = Notify()
        notification.title = "Onkyo Control"
        notification.timeout = 100
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
            if self.receiver.raw("PWRQSTN") != self.powerOn:
                self.receiver.raw(self.powerOn)  
            if self.receiver.raw("SLIQSTN") != self.sourcePC:
                self.receiver.raw(self.sourcePC)
            with self.monitors as monitor:
                input_source_raw: int = monitor.get_input_source()
                if (InputSource(input_source_raw).name != self.defaultInput):
                   monitor.set_input_source(self.monitorDP)
                   self.noti("Monitor Input Changed to Default")
                else: 
                    self.noti("Monitor Default Input")
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
            self.current_volume = self.receiver.raw("MVLQSTN")
            if self.current_volume and "MVL" in self.current_volume:
                hex_vol = self.current_volume.split("MVL")[-1][:2]
                self.current_volume = int(hex_vol, 16)

                self.osd.show(self.current_volume)
            
        except Exception as e:
            self.noti(f"Error changing Volume: {e}")

    def turn_off_AVR_shutdown(self):
        if self.receiver.raw("SLIQSTN") == self.sourcePC:
            self.receiver.raw(self.powerOff)


    def safe_action(self, action):
        try:
            action()
        except Exception as e:
            self.noti(f"Hotkey Error: {e}")

    def setup_hotkeys(self):
        keyboard.add_hotkey('ctrl+alt+p', lambda: self.safe_action(self.toggle_power))
        keyboard.add_hotkey('ctrl+alt+F1', lambda: self.safe_action(lambda: self.change_source(self.sourcePC, self.monitorDP, "Source: PC")))
        keyboard.add_hotkey('ctrl+alt+F2', lambda: self.safe_action(lambda: self.change_source(self.sourceBD, self.monitorHDMI2, "Source: BD")))
        keyboard.add_hotkey('ctrl+alt+F3', lambda: self.safe_action(lambda: self.change_source(self.sourceGame, self.monitorHDMI, "Source: Game")))
        keyboard.add_hotkey('ctrl+alt+F5', lambda: self.safe_action(self.change_HDMI_audio))
        keyboard.add_hotkey('ctrl+alt+up', lambda: self.safe_action(lambda: self.change_volume(self.volumeUP)))
        keyboard.add_hotkey('ctrl+alt+down', lambda: self.safe_action(lambda: self.change_volume(self.volumeDOWN)))
        keyboard.add_hotkey('ctrl+alt+R', lambda: self.safe_action(self.reconnect))
    
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
        try:
            response = ping(self.ip_address, timeout=2)
            if response is None:
                self.noti("Can't reach AVR: Attempting reconnect...")
                self.reconnect()
                return False
            return True
        except Exception as e:
            self.noti(f"Ping error: {e}")
            return False

 

        