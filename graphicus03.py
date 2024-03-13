import sys
import time
from threading import Thread
from queue import Queue
from class_moteurs import Moteurs
from interface import initWindow

#------------Variables------------
queueFromInterface = Queue()
queueFromProcess   = Queue()

#-----------Fonctions------------------------
def process(queueFromInterface, queueFromProcess):    
    """Fonction process(queue x, queue y):
        La fonction contrôle les entrées et sorties du raspberry PI.
    """
    moteurs = Moteurs()
    moteurs.sequence(queueFromInterface)
    moteurs.read_stepper_position(queueFromProcess)
    return

def interface(queueFromInterface, queueFromProcess):
    initWindow(queueFromInterface, queueFromProcess)
    return

#-----------Creation de thread----------------
processThread = Thread(target=process, args=(queueFromInterface, queueFromProcess))
interfaceThread = Thread(target=interface, args=(queueFromInterface, queueFromProcess))

#------------Execution----------
processThread.start()
interfaceThread.start()
processThread.join()
interfaceThread.join()
