#!/usr/bin/python

# Reads from the MCP3008 

import asyncore
import socket
import spidev
import time
import os
import json
import pprint
import Tkinter as tk

try: 
  import RPi.GPIO as GPIO
except RuntimeError:
  print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")

import datetime

# Set up the GPIO ports for reading.
spi = spidev.SpiDev()
spi.open(0,0)

GPIO.setmode(GPIO.BOARD)

# This is for the tach, when I get around to writing it.
GPIO.setup(26, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

# Set up the temp sensors, x and y are positions on the screen. 

channels = {}
channels['a'] = {'name': 'Engine Bay', 'adc': 0, 'x': 320, 'y': 10}
channels['b'] = {'name': '#1 Cylinder', 'adc': 1, 'x': 805, 'y': 10}
channels['c'] = {'name': 'Cabin Temperature', 'adc': 2, 'x': 320, 'y': 345}
channels['d'] = {'name': 'Outside Temperature', 'adc': 3, 'x': 805, 'y': 345}

def set_default(obj):
  if isinstance(obj, set):
     return list(obj)
  raise TypeError

def ReadChannel(channel):
  adc = spi.xfer2([1,(8+channel)<<4,0])
  data = float((adc[1]&3) << 8) + adc[2]
  return data

def ConvertVolts(data,places):
  volts = float(data * 3.3) / float(1023)
  volts = round(volts,places)  
  return volts
  
def ConvertTemp(data,places):
  temp = float((data * 330)/float(1023))-50
  temp = round(temp,places)
  return temp

def readTemps():

  # Read all of the sensors and update the screen.

  for key, value in channels.items():
    level = ReadChannel(value['adc'])
    volts = ConvertVolts(level, 8)
    temp  = ConvertTemp(level, 8)
  
    channels[key]['ltemp']['text'] = "{:.1f}".format((temp*1.8)+32)
  channels['a']['ltemp'].after(8000, readTemps)

# Set up the interface.

root = tk.Tk()

# Formatted for a 720p screen. 

root.title('Vanagon Environmental Monitor')
root.geometry("1280x720+0+0")

# This places a picture of the engine.

wbx = tk.PhotoImage(file="waterbox.gif")
wbxl = tk.Label(image=wbx)
wbxl.pack()
wbxl.place(x = 10, y = (345-177)/2)

# This places a picture of the van.

van = tk.PhotoImage(file="brownvan.gif")
vanl = tk.Label(image=van)
vanl.pack()
vanl.place(x = 10, y = ((345-168)/2) + 320 )

# Draw the interface.

for key, value in channels.items():
  channels[key]['ltemp'] = tk.Label(root, fg='light green', bg='dark green', font="Helvetica 120 bold")
  channels[key]['ltemp'].pack( fill=tk.X, padx=50, pady=50 )
  channels[key]['ltemp'].place( x = channels[key]['x'], y = channels[key]['y'] + 20, width=450, height=300)
  channels[key]['label'] = tk.Label(root, text=channels[key]['name'], fg="light blue", bg="dark blue", font="Helvetica 14 bold");
  channels[key]['label'].pack( fill=tk.X )
  channels[key]['label'].place( x = channels[key]['x'], y = channels[key]['y'], width=450, height=20 )

# And we do the hokey pokey..

readTemps()

root.mainloop()

