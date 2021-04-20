# packages
import math
import re
import keyboard
import mido
import mido.backends.rtmidi
import os
import msvcrt
from threading import Thread
from time import sleep

# static variables
floor = math.floor
press = keyboard.press
release = keyboard.release

currentPort = None

velocityMap = "1234567890qwertyuiopasdfghjklzxc"

letterNoteMap = "1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm"
LowNotes = "1234567890qwert"
HighNotes = "yuiopasdfghj"

sustainToggle = False
MainLoop = True
CloseThread = False

SettingsFileName = "MidiTranslatorSettings"

velocityList = [0, 4, 8, 12,
                16, 20, 24, 28,
                32, 36, 40, 44,
                48, 52, 56, 60,
                64, 68, 72, 76,
                80, 84, 88, 92,
                96, 100, 104, 108,
                112, 116, 120, 124]

# savable variables

SavableSettings = {"sustainEnabled": True, "noDoubles": True, "simulateVelocity": True, "88Keys": True,
                   "sustainCutoff": 63}


# functions


# midi port selection
def select_port():
    global currentPort
    if currentPort:
        currentPort.close()
    print("Select input device:")
    inputports = mido.get_input_names()
    for portNumber, portName in enumerate(inputports):
        print(str(portNumber + 1) + ": " + portName)
    while True:
        selectedport = int(input("(enter a number from 1 to " + str(len(inputports)) + ")\n")) - 1
        if 0 <= selectedport < len(inputports):
            break
        else:
            print("Please select a valid input device.")
    print("Selected " + inputports[selectedport])
    return inputports[selectedport]

  
# velocity index binary search (fixed)
def find_velocity_key(velocity):
    minimum = 0
    maximum = len(velocityList) - 1
    while minimum <= maximum:
        index = (minimum + maximum) // 2
        if index == (0 or len(velocityList) - 1):
            break
        if velocityList[index] < velocity:
            minimum = index + 1
        elif velocityList[index] > velocity:
            maximum = index - 1
        else:
            break
    return velocityMap[index]


# simulate qwerty keypress
def simulate_key(type, note, velocity):
    if not (-15 <= note - 36 <= 88):
        return
    index = note - 36
    key = 0
    try:
        key = letterNoteMap[index]  # C1 is note 36, C6 is note 96
    except:
        pass
    if type == 'note_on':

        if SavableSettings["simulateVelocity"]:
            velocitykey = find_velocity_key(velocity)
            press('alt')
            press(velocitykey)
            release(velocitykey)
            release('alt')

        if 0 <= note - 36 <= 60:
            if SavableSettings["noDoubles"]:
                if re.search('[!@$%^*(]', key):
                    release(letterNoteMap[index - 1])
                else:
                    release(key.lower())
            if re.search('[!@$%^*(]', key):
                press('shift')
                press(letterNoteMap[index - 1])
                release('shift')
            elif key.isupper():
                press('shift')
                press(key.lower())
                release('shift')
            else:
                press(key)
        elif SavableSettings["88Keys"]:
            K = None
            if 20 <= note < 40:
                K = LowNotes[note - 21]
            else:
                K = HighNotes[note - 109]
            if K:
                release(K.lower())
                press('ctrl')
                press(K.lower())
                release('ctrl')

    else:
        if 0 <= note - 36 <= 60:
            if re.search('[!@$%^*(]', key):
                release(letterNoteMap[index - 1])
            else:
                release(key.lower())
        else:
            if 20 <= note < 40:
                K = LowNotes[note - 21]
            else:
                K = HighNotes[note - 109]
            release(K.lower())


# read and interpret midi input
def parse_midi(message):
    global sustainToggle
    if message.type == 'control_change' and SavableSettings["sustainEnabled"]:
        if not sustainToggle and message.value > SavableSettings["sustainCutoff"]:
            sustainToggle = True
            press('space')
        elif sustainToggle and message.value < SavableSettings["sustainCutoff"]:
            sustainToggle = False
            release('space')
    elif message.type == 'note_on' or message.type == 'note_off':
        if message.velocity == 0:
            simulate_key('note_off', message.note, message.velocity)
        else:
            simulate_key(message.type, message.note, message.velocity)


# main program loop
def Main():
    global CloseThread
    print("Now listening to note events on " + str(currentPort) + "...")
    for message in currentPort:
        parse_midi(message)
        if CloseThread:
            break
    CloseThread = False


# settings menu
def Settings():
    global SavableSettings, currentPort
    changing = True
    while changing:
        Clear()
        print('''
Which settings would you like to change?

0. Back

1. Sustain Enabled (''' + str(SavableSettings["sustainEnabled"]) + ''')

2. Double Notes Disabled (''' + str(SavableSettings["noDoubles"]) + ''')

3. Velocity Enabled (''' + str(SavableSettings["simulateVelocity"]) + ''')

4. 88 Keys Enabled (''' + str(SavableSettings["88Keys"]) + ''')

5. Sustain Pedal Cutoff/Offset (''' + str(SavableSettings["sustainCutoff"]) + ''')

6. Change Midi Port (''' + str(currentPort) + ''') ''')
        t = None
        try:
            t = int(msvcrt.getch().decode("utf-8"))
            if t > 6 or t < 0:
                t = None
        except:
            t = None

        if t is not None:
            if t == 0:
                Clear()
                changing = False
            elif t == 1:
                SavableSettings["sustainEnabled"] = not SavableSettings["sustainEnabled"]
            elif t == 2:
                SavableSettings["noDoubles"] = not SavableSettings["noDoubles"]
            elif t == 3:
                SavableSettings["simulateVelocity"] = not SavableSettings["simulateVelocity"]
            elif t == 4:
                SavableSettings["88Keys"] = not SavableSettings["88Keys"]
            elif t == 5:
                SavableSettings["sustainCutoff"] = IntAsk("\nEnter what offset you would like to use (0-127)")
            elif t == 6:
                currentPort = mido.open_input(select_port())

            Save()
        else:
            print('\nError, try again\n')
            sleep(.5)


# load settings from file
def LoadFiles():
    global SavableSettings
    try:
        f = open(SettingsFileName + '.txt', "r")
        it = 0
        setting = None
        for i in f.read().split('\n'):
            it += 1
            if it % 2 == 1:
                setting = i
            else:
                try:
                    SavableSettings[str(setting)] = int(i)
                except:
                    SavableSettings[str(setting)] = i
                    if SavableSettings[str(setting)] == "True":
                        SavableSettings[str(setting)] = True
                    elif SavableSettings[str(setting)] == "False":
                        SavableSettings[str(setting)] = False

        f.close()
    except:
        Save()


# save settings to file
def Save():
    File = open(SettingsFileName + '.txt', 'w')
    it = 0
    for i, v in SavableSettings.items():
        it += 1
        if it != 1:
            File.write('\n' + str(i) + '\n')
        else:
            File.write(str(i) + '\n')
        File.write(str(v))
    File.close()


# clear prints
def Clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# user input
def IntAsk(text):
    var = None
    while var == None:
        try:
            var = int(input(text))
        except:
            print('\nThere was an issue\n')
            var = None

    return var


# initialize settings
try:
    LoadFiles()
    currentPort = mido.open_input(select_port())

    while MainLoop:
        Clear()
        print('   ---Welcome to the menu---\n\n\n1. Run main program\n\n2. Settings')
        t = None
        try:
            t = int(msvcrt.getch().decode("utf-8"))
            if t > 2 or t < 1:
                t = None
        except:
            t = None

        if t:
            Clear()
            if t == 1:
                Clear()
                Thread(target=Main).start()
                sleep(.5)
                input('Main code is now running\nhit enter to go back to the menu at any time')
                CloseThread = True
            elif t == 2:
                Clear()
                Settings()

        else:
            Clear()
            print('There seemed to be an issue')

except Exception as E:
    Clear()
    print('Error detected')
    input(E)
input('\n\nHit enter now to close')
