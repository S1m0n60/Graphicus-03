from queue import Queue
import RPi.GPIO as GPIO
import time
from math import radians
from math import cos
from math import sin

class Moteurs:
    def __init__(self):
        """Initialisation des E/S pour le Raspberry Pi
        """
        # Init stepper
        self.enable_pin1, self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1 = 1,23,20,22,12 # Moteur laser
        self.enable_pin2, self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2 = 1,23,20,22,12 # Moteurs plateau
        self.enable_pin3, self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3 = 1,12,13,14,15 # Moteur verre

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup((self.enable_pin1, self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1), GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup((self.enable_pin2, self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2), GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup((self.enable_pin3, self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3), GPIO.OUT, initial=GPIO.LOW)

        self.limit_switch_pins = [24,25,5,6]  
        GPIO.setup(self.limit_switch_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.stepper_position_queue = Queue()
        self.stepper_angle_queue = Queue()
        self.stepper_position = 0
        self.stepper_angle = 0
        self.angle_rotation = 10

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

    def stop_motors(self):
        """Fonction permettant d'arrêter les moteurs"""
        # Turn off all coils for motor 1
        GPIO.output(self.coil_A1, GPIO.LOW)
        GPIO.output(self.coil_B1, GPIO.LOW)
        GPIO.output(self.coil_C1, GPIO.LOW)
        GPIO.output(self.coil_D1, GPIO.LOW)

        # Turn off all coils for motor 2
        GPIO.output(self.coil_A2, GPIO.LOW)
        GPIO.output(self.coil_B2, GPIO.LOW)
        GPIO.output(self.coil_C2, GPIO.LOW)
        GPIO.output(self.coil_D2, GPIO.LOW)

        # Turn off all coils for motor 3
        GPIO.output(self.coil_A3, GPIO.LOW)
        GPIO.output(self.coil_B3, GPIO.LOW)
        GPIO.output(self.coil_C3, GPIO.LOW)
        GPIO.output(self.coil_D3, GPIO.LOW)

    def move_stepper_motor_forward(self, motor_id, steps, speed):
        """Fonction permettant de faire avancer un moteur pas-à-pas selon une vitesse et un nombre de pas spécifié

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            steps (int): Nombre de pas désiré
            speed (float): Vitesse du moteur désirée (0-1000)
        """
        self.stepper_position_queue.put((motor_id, steps))

        if speed > 525:
            speed = 525

        if motor_id == 1:
            limit_switch_pin1 = 1
            limit_switch_pin2 = 2
        elif motor_id == 2:
            limit_switch_pin1 = 3
            limit_switch_pin2 = 4
        
        coil_sequence = [(1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 1)]
        delay = 1.0 / speed
        step_count = 0
        start_time = time.time()

        while step_count < steps:    
            elapsed_time = time.time() - start_time
            if elapsed_time >= delay:
                coils = coil_sequence[step_count%4]
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                start_time = time.time() 
                step_count += 1 

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
        if speed > 525:
            speed = 525
            
        self.stepper_position_queue.put((motor_id, -steps))
        if motor_id == 1:
            limit_switch_pin1 = 1
            limit_switch_pin2 = 2
        elif motor_id == 2:
            limit_switch_pin1 = 3
            limit_switch_pin2 = 4
        
        coil_sequence = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 1, 1, 0), (1, 0, 1, 0)]
        delay_ = 1.0 / speed
        start_time = time.time()
        step_count = 0

        while step_count < steps:  
            elapsed_time = time.time() - start_time
            if elapsed_time >= delay_:
                coils = coil_sequence[step_count%4]
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                start_time = time.time() 
                step_count += 1 

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
        pas_par_mm = 0.125  # Pas par millimètre de la vis sans fin

        # Calculer le nombre de pas requis
        pas = distance * pas_par_mm * (360 / degres_par_pas)
        pas_int = int(pas)

        if distance > 0:
            self.move_stepper_motor_forward(motor_id, pas_int, speed)
        elif distance < 0:
            self.move_stepper_motor_backwards(motor_id, abs(pas_int), speed)

    def laser_go_to_home(self):
        """Fonction permettant le déplacement du moteur pas-à-pas jusqu'à l'activation d'un des 2 capteurs de fin de course
        """
        motor_id = 1 
           
        self.move_stepper_motor_forward(motor_id, steps=1000, speed=450)

        self.stepper_position = 0

    def move_board_up(self):
        """Fonction permettant de bouger les moteurs 2 et 3 pas-à-pas en même temps pour faire bouger la plateforme vers le haut
        """
        motor_id = 2

        self.move_stepper_motor_forward(motor_id, steps=10000, speed=450)

    def move_board_down(self):
        """Fonction permettant de bouger les moteurs 2 et 3 pas-à-pas en même temps pour faire bouger la plateforme vers le bas
        """
        motor_id = 2

        self.move_stepper_motor_backwards(motor_id, steps=10000, speed=450)

    def move_board_to_pos(self):
        """Fonction permettant de bouger le plateau a la position de depart

        Args:
            queue_radius (float): Rayon récupéré depuis la file d'attente.
        """

        motor_id = 2
        diametre_verre = 2 * self.queue_radius
        hauteur = 200 ############################
        distance_focale = 10 #####################
        position = hauteur - distance_focale - diametre_verre

        self.move_stepper_to_distance(motor_id, position, 450)
   
    def gravure(self):
        """Fonction de séquence de gravure du verre

        Args:
            queue_longueur_verre (float): Longueur du verre récupérée depuis la file d'attente.
            queue_distance_debut_gravure (float): Distance de début de la gravure récupérée depuis la file d'attente.
            queue_button_start (bool): État du bouton de démarrage récupéré depuis la file d'attente.
            queue_radius (float): Rayon récupéré depuis la file d'attente.
        """
        # Récupération des paramètres depuis les queues
        angle_rotation_intermediaire = self.angle_rotation ##########################
        cst_debut = 10

        longueur_totale = 30 ########################
        position_initiale = (longueur_totale / 2 + cst_debut)

        self.move_stepper_to_distance(motor_id=1, distance=position_initiale, speed=600)

        radius = self.queue_radius
        final_position_theta = radians(angle_rotation_intermediaire)
        final_position_x = radius * cos(final_position_theta)
        final_position_y = radius * sin(final_position_theta)

        button_press = self.queue_button_start
        if button_press == "debut*":
            
            self.move_stepper_to_distance(motor_id=1, distance=cst_debut, speed=600)
            self.stepper_position_queue.put((1, cst_debut))

            self.move_stepper_motor_forward(motor_id=3, steps=int(angle_rotation_intermediaire), speed=600)
            self.stepper_angle_queue.put(angle_rotation_intermediaire)
            current_position_x, current_position_y = self.read_stepper_position()
            
            self.move_stepper_to_distance(motor_id=1, distance=-cst_debut, speed=600)
            self.stepper_position_queue.put((1, -cst_debut))

            if current_position_x >= final_position_x and current_position_y <= final_position_y:
                self.stop_motors()

    def read_stepper_position(self, processThread):
        """Fonction permettant de mettre les valeurs de positions parcourues en temps réel par le moteur 2 et la position d'angle du moteur 3 dans les files d'attente."""

        while not self.stepper_position_queue.empty():
            motor_id, steps = self.stepper_position_queue.get()
            if motor_id == 2:
                stepper_position += steps
            elif motor_id == 3:
                angle_position += steps
    
            self.stepper_position_queue.put((motor_id, steps))
            self.stepper_angle_queue.put((motor_id, steps))
            processThread.put = ([self.stepper_position_queue, self.stepper_angle_queue])
  
    def queue_read(self, queue_in):
        self.queue_button_start = queue_in[0]
        self.queue_gravx = queue_in[1]
        self.queue_gravy = queue_in[2]
        self.queue_radius = queue_in[3]

    def sequence(self,queue_in):
        self.enable_stepper_motor(1)
        self.enable_stepper_motor(2)
        self.enable_stepper_motor(3)
        self.queue_read(queue_in)
        self.laser_go_to_home()
        self.move_board_down()
        self.move_board_to_pos()
        self.gravure()
        self.laser_go_to_home()
        self.move_board_down()

