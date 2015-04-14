
# This code should be deployed on all working door nodes. 
# The raspi_node is the brains of this has a different address
# 
from synapse.platforms import *
from synapse.switchboard import *

# Pin Definitions check the schematic for any changes.
PIN_STATE = 0
LED_PIN = 4
EXIT_BUTTON = 12
DOOR_BELL_BUTTON = 15
DOOR_PIN = 9
COUNTER = 0
raspi_node = "\x00\x00\x20" #portal node"\x5E\x30\xAD"

@setHook(HOOK_STARTUP)
def startupEvent():
    """Executed when the device boots up, this initializes the hardware and begins monitoring the button."""
    # pin dir True is out, False is input
    setPinDir(EXIT_BUTTON, False)
    setPinDir(DOOR_BELL_BUTTON, False)
    setPinDir(LED_PIN, True)
    setPinDir(DOOR_PIN, True)
    monitorPin(EXIT_BUTTON, True)
    monitorPin(DOOR_BELL_BUTTON, True)
    initUart(1,9600)
    crossConnect(DS_UART1, DS_STDIO)


@setHook(HOOK_STDIN)
def sendData(data):
    print "Sending data"
    rpc(raspi_node, 'callback', 'unlockDoor', 'checkDoor', data)

def unlockDoor(should_open):
    print "door unlocked"
    print should_open
    if should_open == "True":
        lightOpenDoor()


def countDown(): #roughly 1-2s
    global COUNTER
    COUNTER = 6500000
    while COUNTER > 0:
        COUNTER = COUNTER - 1

def changePinState():
    global PIN_STATE
    if PIN_STATE == 0:
        PIN_STATE = 1
    elif PIN_STATE == 1:
        PIN_STATE = 0

def lightOpenDoor():
    changePinState()
    openDoor()
   # lightLed()
    countDown()
    countDown()
    countDown()
    countDown()
    changePinState()
    openDoor()
   # lightLed()
   
def openDoor():
    writePin(DOOR_PIN, PIN_STATE)
    
def lightLed():
    writePin(LED_PIN, PIN_STATE)

@setHook(HOOK_GPIN)
def buttonEvent(pin, isSet):    
    """This event handler runs when the select switch (button) is pressed"""
    if pin == EXIT_BUTTON:
        if isSet == True:
            lightOpenDoor
            print EXIT_BUTTON
    if pin == DOOR_BELL_BUTTON:
        if isSet == True:
            print DOOR_BELL_BUTTON
            rpc(raspi_node, 'dingDong', pin)

