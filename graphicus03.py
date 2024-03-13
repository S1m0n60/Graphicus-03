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
    moteurs = Moteurs(queueFromInterface, queueFromProcess)
    stop = False
    while not stop:
        if not queueFromInterface.empty():
            lecture = queueFromInterface.get_nowait()
            if type(lecture) == str:
                stop = (lecture == "stop")
            elif type(lecture) == list:
                moteurs.queue_button_start = lecture[0]
                moteurs.queue_gravx = lecture[1]
                moteurs.queue_gravy = lecture[2]
                moteurs.queue_radius = lecture[3]
                break
    moteurs.sequence()
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
