from queue import Queue
import RPi.GPIO as GPIO
from time import *

class Moteurs:
    def __init__(self):
        """Initialisation des E/S pour le Raspberry Pi
        """
        # Init stepper
        self.enable_pin1, self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1 = 1,23,20,22,12
        self.enable_pin2, self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2 = 1,23,20,22,12
        self.enable_pin3, self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3 = 11, 12, 13, 14, 15

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup((self.enable_pin1, self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1), GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup((self.enable_pin2, self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2), GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup((self.enable_pin3, self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3), GPIO.OUT, initial=GPIO.LOW)

        self.limit_switch_pins = [24,25,5,6]  
        GPIO.setup(self.limit_switch_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.stepper_position_queue = Queue()
        self.stepper_position = 0

    def is_limit_switch_triggered(self, switch_id):
        """Fonction pour vérifier si un des capteurs de fin de course est activé

        Args:
            switch_id (int): Numéro d'identification du capteur de fin de course (1-4)

        Returns:
            int: 0 - Capteur de fin de course non-actif
                 1 - capteur de fin de course actif
        """
        return GPIO.input(self.limit_switch_pins[switch_id-1])
    
    def enable_stepper_motor(self, motor_id):
        """Fonction permettant d'activer un des moteurs pas-à-pas

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
        """
        enable_pin = self.get_enable_pin(motor_id)
        GPIO.output(enable_pin, GPIO.HIGH)

    def disable_stepper_motor(self, motor_id):
        """Fonction permettant de désactiver un des moteurs pas-à-pas

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
        """
        enable_pin = self.get_enable_pin(motor_id)
        GPIO.output(enable_pin, GPIO.LOW)

    def get_enable_pin(self, motor_id):
        """Fonction permettant de retourner la pin d'activation du moteur concerné

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)

        Returns:
            int: Valeur de la pin correspondante à l'identifiant du moteur en args
        """
        if motor_id == 1:
            return self.enable_pin1
        elif motor_id == 2:
            return self.enable_pin2
        elif motor_id == 3:
            return self.enable_pin3
        else:
            print(f"Invalid motor_id: {motor_id}")
            return None

    def move_stepper_motor_forward(self, motor_id, steps, speed):
        """Fonction permettant de faire avancer un moteur pas-à-pas selon une vitesse et un nombre de pas spécifié

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            steps (int): Nombre de pas désiré
            speed (float): Vitesse du moteur désirée (0-1000)
        """
        
        self.stepper_position_queue.put((motor_id, steps))

        if motor_id == 1:
            limit_switch_pin1 = 1
            limit_switch_pin2 = 2
        elif motor_id == 2:
            limit_switch_pin1 = 3
            limit_switch_pin2 = 4
            return
        
        coil_sequence = [(1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 1)]
        delay = 1.0 / speed

        for _ in range(steps):
            for coils in coil_sequence:
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                sleep(delay)
                if self.is_limit_switch_triggered(limit_switch_pin1) == 1 or self.is_limit_switch_triggered(limit_switch_pin2) == 1:
                    return

            self.stepper_position += 1

    def move_stepper_motor_backwards(self, motor_id, steps, speed):
        """Fonction permettant de faire reculer un moteur pas-à-pas selon une vitesse et un nombre de pas spécifié

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            steps (int): Nombre de pas désiré
            speed (float): Vitesse du moteur désirée (0-1000)
        """
       
        self.stepper_position_queue.put((motor_id, -steps))
        if motor_id == 1:
            limit_switch_pin1 = 1
            limit_switch_pin2 = 2
        elif motor_id == 2:
            limit_switch_pin1 = 3
            limit_switch_pin2 = 4
            return
        
        coil_sequence = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 1, 1, 0), (1, 0, 1, 0)]
        delay = 1.0 / speed

        for _ in range(steps):
            for coils in coil_sequence:
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                sleep(delay)
                if self.is_limit_switch_triggered(limit_switch_pin1) == 1 or self.is_limit_switch_triggered(limit_switch_pin2) == 1:
                    return

            self.stepper_position -= 1

    def get_coil_pins(self, motor_id):
        """Fonction utilisée dans les fonctions move_stepper_motor_forward et move_stepper_motor_backwards pour retourner les 
           pins du moteur spécifié

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)

        Returns:
            _type_: _description_
        """
        if motor_id == 1:
            return (self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1)
        elif motor_id == 2:
            return (self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2)
        elif motor_id == 3:
            return (self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3)
        else:
            return ()

    def move_stepper_to_distance(self, motor_id, distance, speed):
        """Déplacer le moteur pas-à-pas à une distance spécifiée en millimètres.

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3).
            distance (float): Distance à parcourir en millimètres.
            speed (float): Vitesse désirée du moteur (0-1000).
        """
        # Constantes
        degres_par_pas = 1.8  # Degrés par pas du moteur
        pas_par_mm = 0.5  # Pas par millimètre de la vis sans fin

        # Calculer le nombre de pas requis
        pas = (distance * pas_par_mm * (360 / degres_par_pas))/4
        pas_int = int(pas)
        #print(pas_int)

        if distance > 0:
            self.move_stepper_motor_forward(motor_id, pas_int, speed)
        elif distance < 0:
            self.move_stepper_motor_backwards(motor_id, abs(pas_int), speed)


    def laser_go_to_home(self):
        """Fonction permettant le déplacement du moteur pas-à-pas jusqu'à l'activation d'un des 2 capteurs de fin de course
        """
        motor_id = 1 
        self.enable_stepper_motor(motor_id)
           
        self.move_stepper_motor_forward(motor_id, steps=1000, speed=600)

        self.stepper_position = 0
        self.disable_stepper_motor(motor_id)

    def move_board_up(self):
        """Fonction permettant de bouger les moteurs 2 et 3 pas-à-pas en même temps pour faire bouger la plateforme vers le haut
        """
        motor_id = 2
        self.enable_stepper_motor(motor_id)

        self.move_stepper_motor_forward(motor_id, steps=10000, speed=600)

        self.disable_stepper_motor(motor_id)

    def move_board_down(self):
        """Fonction permettant de bouger les moteurs 2 et 3 pas-à-pas en même temps pour faire bouger la plateforme vers le bas
        """
        limit_switch_id1 = 3
        limit_switch_id2 = 4

        limit_switch_pin1 = self.limit_switch_pins[limit_switch_id1 - 1]
        limit_switch_pin2 = self.limit_switch_pins[limit_switch_id2 - 1]

        motor_id = 2
        self.enable_stepper_motor(motor_id)


        while (self.is_limit_switch_triggered(limit_switch_pin1) == 0 or self.is_limit_switch_triggered(limit_switch_pin2) == 0):
            self.move_stepper_motor_backwards(motor_id, steps=1, speed=10)

        self.disable_stepper_motor(motor_id)
    
    def gravure(self, queue_longueur_verre, queue_distance_debut_gravure, queue_angle_rotation_intermediaire, queue_marque_fin_gravure):
        """Fonction permettant de réaliser la gravure sur le verre.

        Args:
            queue_longueur_verre (Queue): File d'attente pour la longueur du verre en mm.
            queue_distance_debut_gravure (Queue): File d'attente pour la distance du début de la gravure à partir du centre du verre en mm.
            queue_angle_rotation_intermediaire (Queue): File d'attente pour l'angle de rotation intermédiaire en degrés.
            queue_marque_fin_gravure (Queue): File d'attente pour la variable indiquant la fin de la gravure.
            queue_positions (Queue): File d'attente pour stocker les positions du moteur.
        """
        # Récupération des paramètres depuis les queues
        longueur_verre = queue_longueur_verre.get()
        distance_debut_gravure = queue_distance_debut_gravure.get()
        angle_rotation_intermediaire = queue_angle_rotation_intermediaire.get()
        marque_fin_gravure = queue_marque_fin_gravure.get()

        # Position initiale du moteur 1
        longueur_totale = 30
        position_initiale = (longueur_totale/2 + longueur_verre / 2 + distance_debut_gravure)

        # Position du moteur 1 pour débuter la gravure
        self.move_stepper_to_distance(motor_id=1, distance=position_initiale, speed=600)

        while not marque_fin_gravure:
            # Aller
            self.move_stepper_to_distance(motor_id=1, distance=longueur_verre, speed=600)
            self.stepper_position_queue.put((1, longueur_verre))
            # Retour
            self.move_stepper_to_distance(motor_id=1, distance=-longueur_verre, speed=600)
            self.stepper_position_queue.put((1, -longueur_verre))
            # Rotation moteur 3
            self.move_stepper_motor_forward(motor_id=3, steps=int(angle_rotation_intermediaire), speed=600)
            self.angle_position_queue.put(angle_rotation_intermediaire)

        print("Gravure terminée.")
       
    def read_stepper_position(self):
        """Fonction permettant de retourner les valeurs de positions parcourues en temps réel par le moteur 2 et la position d'angle du moteur 3.

        Returns:
            tuple: (Position moteur 2, Position d'angle moteur 3)
        """
        stepper_position = 0
        angle_position = 0

        # Parcourir les éléments de la file d'attente pour obtenir les positions en temps réel
        while not self.stepper_position_queue.empty():
            motor_id, steps = self.stepper_position_queue.get()
            if motor_id == 2:
                stepper_position += steps
        while not self.angle_position_queue.empty():
            angle_position = self.angle_position_queue.get()

        return stepper_position, angle_position


testmoteur = Moteurs()
testmoteur.enable_stepper_motor(1)
#testmoteur.enable_stepper_motor(4)
#testmoteur.move_stepper_motor_forward(4,1,10)
#testmoteur.move_stepper_motor_backwards(1,700,750)
#testmoteur.move_stepper_motor_forward(1,1000,750)
#print(testmoteur.is_limit_switch_triggered(2))
#testmoteur.set_motor_speed(10)
#testmoteur.read_motor_state()
#testmoteur.read_stepper_position()
#testmoteur.enable_torque()
#testmoteur.disable_stepper_motor(1)
#testmoteur.disable_stepper_motor(4)
testmoteur.move_stepper_to_distance(1,-20,600)
#testmoteur.move_stepper_motor_backwards(1,1000,100)
#while True:
    #print(testmoteur.is_limit_switch_triggered(2))
     #testmoteur.read_stepper_position()
#testmoteur.set_motor_speed(15)
#testmoteur.move_board_up()
#testmoteur.laser_go_to_home()
