import sys
import time
from threading import Thread
from queue import Queue
from class_moteurs import Moteurs

moteurs = Moteurs(1,1)

#-----------Fonctions------------------------
def motor1(moteurs):    

    while True:
        moteurs.move_stepper_motor_forward(1,1000,450)
        moteurs.move_stepper_motor_backwards(1,1000,450)
        time.sleep(0.05)

def motor2(moteurs):

    while True:
        moteurs.move_board_up()
        moteurs.move_board_down()
        time.sleep(0.05)

def motor3(moteurs):

    while True:
        moteurs.move_stepper_motor_forward(3,500,250)
        moteurs.move_stepper_motor_backwards(3,500,250)
        time.sleep(0.05)
        
#-----------Creation de thread----------------
motor1Thread = Thread(target=motor1, args=moteurs)
motor2Thread = Thread(target=motor2, args=moteurs)
motor3Thread = Thread(target=motor3, args=moteurs)

#------------Execution----------
motor1Thread.start()
motor2Thread.start()
motor3Thread.start()
motor1Thread.join()
motor2Thread.join()
motor3Thread.join()