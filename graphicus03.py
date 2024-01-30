import sys
import time
from threading import Thread
from queue import Queue

#------------Variables------------
queueFromInterface = Queue()
queueFromProcess   = Queue()


#-----------Fonctions------------------------
def process(queueFromInterface, queueFromProcess):
    """Fonction process(queue x, queue y):
        La fonction contrôle les entrées et sorties du raspberry PI.
    """
    

    return

def interface(queueFromInterface, queueFromProcess):
    """Fonction interface(queue x, queue y):
        La fonction contrôle l'interface utilisateur.
    """
    return

#-----------Creation de thread----------------
processThread = Thread(target=process, args=(queueFromInterface, queueFromProcess))
interfaceThread = Thread(target=interface, args=(queueFromInterface, queueFromProcess))

#------------Execution----------
processThread.start()
interfaceThread.start()
processThread.join()
interfaceThread.join()
