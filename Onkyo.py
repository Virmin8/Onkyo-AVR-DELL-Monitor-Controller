import keyboard
import eiscp
import time
from plyer import notification
from monitorcontrol import get_monitors

receiver = eiscp.eISCP('192.168.1.150')

quit_program = False

power_state= receiver.raw("PWRQSTN")
hdmiAudio_state= receiver.raw("HAOQSTN")

sourceBD = "SLI10"
sourcePC= "SLI05"
sourceGame = "SLI02"

zoneDefault = "SLZ23"
zoneBD = "SLZ10"
zoneGame = "SLZ02"

powerOn = "PWR01"
powerOff = "PWR00"

volumeUP = "MVLUP"
volumeDOWN= "MVLDOWN"
hdmiAudioOn= "HAO01"
hdmiAudioOff= "HAO00"

monitorDP = 15
monitorHDMI= 17
monitorHDMI2= 18

def noti(message_user:str):
    tt="Integra"
    ti=10
    an="Onkyo Script"
    notification.notify(title=tt,message=message_user, timeout=ti, app_name=an)

def moni(input):
    try:
        monitors = get_monitors()
        with monitors[0] as monitor:
            monitor.set_input_source(input)
    except Exception as e:
        noti(f"Error changing monitor input: {e}")
    
try:
    receiver.raw(powerOn)  
    receiver.raw(sourcePC)
    receiver.raw(zoneDefault)
    moni(monitorDP)
    noti("Switched On")
    receiver.raw(hdmiAudioOff)
except Exception as e:
    noti("Error switching on: {e}")



def quit_program_func():
    global quit_program
    quit_program = True
    
def togglePower():
    global power_state
    power_state = receiver.raw("PWRQSTN")
    try:
        if power_state == powerOn:
            receiver.raw(powerOff)  # Turn off
            noti("Power: OFF")
            power_state = receiver.raw("PWRQSTN")

        else:
            receiver.raw(powerOn)  # Turn on
            noti("Power: ON")
            power_state = receiver.raw("PWRQSTN")

        time.sleep(1)
    except Exception as e:
            noti(f"Error toggling power: {e}")

def changeSource(source,input,message):
    try:
        receiver.raw(hdmiAudioOff)  
        time.sleep(2)
        receiver.raw(source)  
        noti(message)
        moni(input)
        time.sleep(1)
    except Exception as e:
            noti(f"Error toggling Source: {e}")

def changeZone(zone,message):
    try:
        receiver.raw(zone) 
        noti(message)
        time.sleep(1)
    except Exception as e:
        noti(f"Error switching to Source: {e}")

def changeHDMIAudio():
    global hdmiAudio_state
    hdmiAudio_state= receiver.raw("HAOQSTN")
    try:
        if hdmiAudio_state == hdmiAudioOn:
            receiver.raw(hdmiAudioOff)  
            noti("HDMI Audio: OFF")
            hdmiAudio_state= receiver.raw("HAOQSTN")

        else:
            receiver.raw(hdmiAudioOn)  # Turn on
            noti("HDMI Audio: ON")
            hdmiAudio_state= receiver.raw("HAOQSTN")

        time.sleep(1)
    except Exception as e:
            noti(f"Error toggling power: {e}")

def changeVolume(change):
    try:
        receiver.raw(change) 
    except Exception as e:
        noti(f"Error changing Volume: {e}")

keyboard.add_hotkey('ctrl+alt+p', togglePower)
keyboard.add_hotkey('ctrl+alt+q', quit_program_func)
keyboard.add_hotkey('ctrl+alt+F1', lambda: changeSource(sourcePC,monitorDP, "Source: PC"))
keyboard.add_hotkey('ctrl+alt+F2', lambda: changeSource(sourceBD,monitorHDMI2, "Source: BD"))
keyboard.add_hotkey('ctrl+alt+F3', lambda: changeSource(sourceGame,monitorHDMI, "Source: Game"))
keyboard.add_hotkey('ctrl+alt+F5', lambda: changeZone(zoneDefault,"Zone 2: PC"))
keyboard.add_hotkey('ctrl+alt+F6', changeHDMIAudio)
keyboard.add_hotkey('ctrl+alt+up', lambda: changeVolume(volumeUP))
keyboard.add_hotkey('ctrl+alt+down', lambda: changeVolume(volumeDOWN))

while not quit_program:
    time.sleep(0.1)

receiver.disconnect()