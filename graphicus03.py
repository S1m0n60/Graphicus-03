import sys
import time
from threading import Thread
from queue import Queue
from interface import initWindow

#------------Variables------------
queueFromInterface = Queue()
queueFromProcess   = Queue()
#-----------Fonctions------------------------
def process(queueFromInterface, queueFromProcess):    
    """Fonction process(queue x, queue y):
        La fonction contrôle les entrées et sorties du raspberry PI.
    """
    stop = False
    height = 0
    width = 0
    while not stop :
        lecture = queueFromInterface.get()
        if type(lecture) == str :
            print(lecture)
            split_lect = lecture.split("-")
            print(split_lect)
            if split_lect[0] == "debut":
                width  = int(split_lect[1])
                height = int(split_lect[2])
                stop = True
                
    for i in range (0, width):
        for y in range (0, height):
            queueFromProcess.mutex.acquire()
            # print([i, y])
            queueFromProcess.mutex.release()
            queueFromProcess.put([i, y])
            time.sleep(0.0001)
    queueFromProcess.put("finis")
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
