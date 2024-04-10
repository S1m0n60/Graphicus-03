import time
from threading import Thread
from queue import Queue
from moteurs import Moteurs

moteurs = Moteurs(1,1)

#-----------Fonctions------------------------
def motor1(moteurs):    

    while True:
        time.sleep(1)
        moteurs.move_board_up()
        time.sleep(1)
        moteurs.move_board_down()
        time.sleep(1)

def motor3(moteurs):

    while True:
        moteurs.move_stepper_motor_forward(3,500,200)
        moteurs.move_stepper_motor_forward(3,500,350)
        moteurs.move_stepper_motor_backwards(3,500,75)
        moteurs.move_stepper_motor_backwards(3,500,100)
        time.sleep(1)

#-----------Creation de thread----------------
motor1Thread = Thread(target=motor1, args=[moteurs])
motor3Thread = Thread(target=motor3, args=[moteurs])

#------------Execution----------
motor1Thread.start()
motor3Thread.start()
motor1Thread.join()
motor3Thread.join()