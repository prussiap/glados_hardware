"""
This is the brains that gets rfid signals from the synapse door nodes and makes the http request to glados server
"""
#if audio doesn't play try below to get audio through headphones
# sudo amixer cset numid=3 1
import pygame #pygame for audio and any other game interaction
import struct
import logging #python logging
from snapconnect import snap #this is the synapse library
import httplib2 # to make http connect to glados2 server
import json
import RPi.GPIO as GPIO #wiring pi GPIO library access to pi pins
com = ""
log = logging.getLogger("GladosClient")

#open auth key
with open('auth.json') as data_file:
  data = json.load(data_file)

auth_key = data["AESKEY"]

#init http
h = httplib2.Http(".cache")
gheaders = {'cache-control':'no-cache'}

#init onde addresses
otherNodeAddr = '\x5E\x34\x89' #lounge door

#init pygame audio
audio_files = ["audio/door_01.wav",
                "audio/door_02.wav",
                "audio/door_03.wav",
                "audio/door_04.wav"
                ]

def load_sound(file):
  sound = pygame.mixer.Sound(file)
  sound.set_volume(1.0)
  return sound

pygame.init()
my_sound = load_sound(audio_files[0])

#GPIO settings
GPIO.setmode(GPIO.BCM) # Use same pin numbers as on pi header
GPIO.setwarnings(False)
TEST_DOOR_BUZZER = 22
GPIO.setup(TEST_DOOR_BUZZER, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # put arduino input pin as pull up

def unpack_hwaddr(my_byte):
  good_addr = "%x%x%x" % struct.unpack("BBB", my_byte)
  return good_addr.upper()

#url building for fob access

def build_url(fob,door):
  url1 = "http://glados.flipstone.com/open?fobKey="
  url2 = "&doorAddress="
  return url1 + fob + url2 + door

def log_this(msg= "GladosClient: ", log_stuff= ""):
  log.info(msg + str(log_stuff))

def dingDong(data):
  pygame.mixer.music.load(audio_files[0])
  pygame.mixer.music.play(0)
  log_this("DingDong: ", data)

def openDoor(pin):
  com.rpc(otherNodeAddr,'lightOpenDoor')
  log_this("openDoor: pin ", pin)

def convertFobToDecimal(fob = ""):
  if (fob != ""):
    log.info(struct.unpack('14b',fob))
    return "000" + str(int(fob[4:12],16))
  else:
    return ""

def checkDoor(fob):
  log_this("GladosClient has raw fob: ", fob)
  fob_key = convertFobToDecimal(fob)
  log_this("GladosClient has converted fob: ", fob_key)
  good_hwaddr = unpack_hwaddr(com.rpc_source_addr())
  log_this("GladosClient with this address contacted us: " , good_hwaddr)

  content = ""
  if fob_key != "": #== "0C0033AB56C2":
    (resp, content) = h.request(build_url(fob_key,good_hwaddr), "GET", headers = gheaders) #
    parsed_content = json.loads(content)
    log_this("GladosClient can_open:", str(parsed_content['canOpen']) )
    return str(parsed_content['canOpen'])

funcdir = {
            'checkDoor': checkDoor,
            'openDoor': openDoor,
            'dingDong': dingDong
            }

GPIO.add_event_detect(TEST_DOOR_BUZZER, GPIO.RISING, callback=openDoor, bouncetime=300) #Interrupt when Pi pin input goes HIGH/LOW
if __name__ == '__main__':
  logging.basicConfig(level=logging.INFO) # print logging messages to STDOUT
  com = snap.Snap(funcs=funcdir)
  com.accept_tcp()
  com.open_serial(snap.SERIAL_TYPE_RS232, "/dev/ttyUSB0")
  com.save_nv_param(snap.NV_AES128_ENABLE_ID, snap.ENCRYPTION_TYPE_AES128)
  com.save_nv_param(snap.NV_AES128_KEY_ID, auth_key)
  while True:
    com.poll()
  com.stop_accepting_tcp()

