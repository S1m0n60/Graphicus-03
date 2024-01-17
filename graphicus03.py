import sys
import time
from threading import Thread
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

#------------Set Inputs & Outputs------------
GPIO.setmode(GPIO.BCM)

GPIO.setup(laser,GPIO.OUT, initial=0)
GPIO.setup(lsAxisX,GPIO.IN)
GPIO.setup(lsAxisXX,GPIO.IN)
GPIO.setup(lsAxisY,GPIO.IN)
GPIO.setup(lsAxisYY,GPIO.IN)
GPIO.setup(lsAxisZ,GPIO.IN)

#-----------Fonctions------------------------
def process(moteur.main()):
    return

def interface(interface.main()):
    return


#------------Boucle principale------------
while mainInit:

    processThread = Thread(target=process)
    interfaceThread = Thread(target=interface)

    processThread.start()
    interfaceThread.start()
    






GPIO.cleanup()
"""