# miditoqwerty
Translates MIDI input to QWERTY for playing virtual piano. Developed for VPV2 by shizuhaki and brianops1.

While this program will work for other virtual piano sites/games, features such as sustain, velocity, and 88 key support **will** need to be disabled from the settings menu, as currently only VPV2 supports them.

The program is developed for and on Windows 10, and may encounter issues on other OSs.

## Instructions for use:
1. Turn on piano and connect the MIDI cable to the computer.
2. Boot the .py and select the MIDI from the detected input devices.
3. Change settings by hitting "2", or start the program by hitting "1".

A settings file named "MidiTranslatorSettings.txt" will be created in the same folder as the .py on first startup.

## Frequently Asked Questions
- Computer is detecting the file as a virus?
  - Antivirus is detecting the method to simulate keypresses as a possible keylogger/trojan. The source code may be reviewed to show that it is not.
- MIDI was not detected by the program?
  - Ensure that the MIDI was on and plugged in before running the program.
- "MidiInWinMM::openPort: error creating Windows MM MIDI input port."?
  - Another program/site is already attempting to read MIDI input from the same device (i.e. PianoRhythm, another instance of miditoqwerty, etc.). Close all of these then reboot the program.
- Computer (Windows) beeps every time a note is pressed?
  - The program uses ALT+KEY to simulate velocity. Either turn off velocity in the settings or disable the Windows default beep sound.
- MIDI has velocity but does not work in program?
  - Another app/program/site/etc. may be sinking ALT+KEY. Either turn off velocity in the settings or disable/change the settings of programs that are doing so.
