import sys
import time
from threading import Thread
from queue import Queue
#import RPi.GPIO as GPIO -- une librarie seulement installable sur le raspberryPi
#import moteur
#import interface

"""
#------------Constants------------
laser    = 1
lsAxisX  = 2
lsAxisXX = 3
lsAxisY  = 4
lsAxisYY = 5
lsAxisZ  = 3

#------------Variables------------
mainInit = True
queueFromInterface = Queue()
queueFromProcess   = Queue()

#------------Set Inputs & Outputs------------
GPIO.setmode(GPIO.BCM)

GPIO.setup(laser,GPIO.OUT, initial=0)
GPIO.setup(lsAxisX,GPIO.IN)
GPIO.setup(lsAxisXX,GPIO.IN)
GPIO.setup(lsAxisY,GPIO.IN)
GPIO.setup(lsAxisYY,GPIO.IN)
GPIO.setup(lsAxisZ,GPIO.IN)

#-----------Fonctions------------------------
def process(queueFromInterface, queueFromProcess):

    return

def interface(queueFromInterface, queueFromProcess):
    return

#-----------Creation de thread----------------
processThread = Thread(target=process, arg=(queueFromInterface, queueFromProcess))
interfaceThread = Thread(target=interface, arg=(queueFromInterface, queueFromProcess))

#------------Boucle principale----------
while mainInit:


    processThread.start()
    interfaceThread.start()

    processThread.join()
    interfaceThread.join()
    






GPIO.cleanup()
"""