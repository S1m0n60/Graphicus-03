from queue import Queue
import RPi.GPIO as GPIO
import time
from math import pi

# from icecream import ic


# def output_to_file(text):
#     with open("DEBUG_interface.txt", "a") as f:
#         f.write(text + "\n")

# def init_logging_file():
#     with open("DEBUG_interface.txt", "w") as f:
#         f.write("")
# 
# init_logging_file
# ic.configureOutput(prefix="Debug ~ ", outputFunction=output_to_file)


class Moteurs:
    def __init__(self, queue_in : Queue, queue_out : Queue):
        """Initialisation de l'objet moteur, initialisation des entrées/sorties du Raspberry Pi,
        appel des fonctions de calibration de la machine.

        Args:
            queue_in (Queue): File synchronisé pour les entrées provenant de l'interface
            queue_out (Queue): File synchronisé pour les sorties provenant des moteurs
        """
        super(Moteurs, self).__init__()

        self.enable_pin1, self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1 = 1,23,20,22,12 
        self.enable_pin2, self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2 = 1,4,13,27,21 
        self.enable_pin3, self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3 = 1,17,9,18,10 
        self.LASER_pin = 16

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup((self.enable_pin1, self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1), GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup((self.enable_pin2, self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2), GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup((self.enable_pin3, self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3), GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.LASER_pin, GPIO.OUT, initial=GPIO.LOW)
        self.limit_switch_pins = [24,25,5,6]  
        GPIO.setup(self.limit_switch_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.stepper_position_queue = Queue()
        self.stepper_angle_queue = Queue()
        self.queue_out = queue_out
        self.queue_in = queue_in
        self.stepper_position = [0,0,0]
        self.stepper_angle = 0
        self.angle_rotation = 1.8

        self.queue_button_start = False
        self.queue_gravx = 0
        self.queue_gravy = 0
        self.queue_radius = 0
        self.laser_control = {}
        self.no_limit3 = 0

        self.enable_stepper_motor(1)
        self.enable_stepper_motor(2)
        self.enable_stepper_motor(3)
        self.laser_go_to_home()
        self.move_board_down()

    def is_limit_switch_triggered(self, switch_id):
        """Fonction permettant la vérification de l'état d'un capteur de fin de course.
        Une moyenne sur 10 valeurs est effectué afin d'éviter les fausses valeurs.

        Args:
            switch_id (int): Identifiant de l'interrupteur de fin de course (1-4)

        Returns:
            bool: True si le capteur de fin est activé, False sinon
        """
        readings = []
        for _ in range (10):
            readings.append(GPIO.input(self.limit_switch_pins[switch_id-1]))
        return all(readings)
    
    def enable_stepper_motor(self, motor_id):
        """Fonction permettant l'activation du moteur pas-à-pas spécifié

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
        """
        enable_pin = self.get_enable_pin(motor_id)
        GPIO.output(enable_pin, GPIO.HIGH)

    def disable_stepper_motor(self, motor_id):
        """Fonction permettant la désactivation du moteur pas-à-pas spécifié

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
        """
        enable_pin = self.get_enable_pin(motor_id)
        GPIO.output(enable_pin, GPIO.LOW)

    def get_enable_pin(self, motor_id):
        """Fonction permettant la récupération du numéro de broche de contrôle pour les moteurs pas-à-pas

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)

        Returns:
            int: Numéro de broche de contrôle du moteur spécifié
        """
        if motor_id == 1:
            return self.enable_pin1
        elif motor_id == 2:
            return self.enable_pin2
        elif motor_id == 3:
            return self.enable_pin3

    def stop_motors(self):
        """Fonction permettant la désactivation des moteurs en désactivant toutes les bobines
        """
        GPIO.output(self.coil_A1, GPIO.LOW)
        GPIO.output(self.coil_B1, GPIO.LOW)
        GPIO.output(self.coil_C1, GPIO.LOW)
        GPIO.output(self.coil_D1, GPIO.LOW)

        GPIO.output(self.coil_A2, GPIO.LOW)
        GPIO.output(self.coil_B2, GPIO.LOW)
        GPIO.output(self.coil_C2, GPIO.LOW)
        GPIO.output(self.coil_D2, GPIO.LOW)

        GPIO.output(self.coil_A3, GPIO.LOW)
        GPIO.output(self.coil_B3, GPIO.LOW)
        GPIO.output(self.coil_C3, GPIO.LOW)
        GPIO.output(self.coil_D3, GPIO.LOW)

    def move_stepper_motor_forward(self, motor_id, steps, speed):
        """Fonction permettant de faire avancer le moteur pas-à-pas spécifié d'un certain nombre de pas à une vitesse donnée

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            steps (int): Nombre de pas à effectuer
            speed (int): Vitesse de déplacement du moteur
        """
        if speed > 525:
            speed = 525

        if motor_id == 1:
            limit_switch_pin2 = 2
        elif motor_id == 2:
            limit_switch_pin2 = 3
        elif motor_id == 3:
            limit_switch_pin2 = self.no_limit3
        
        coil_sequence = [(1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 1)]
        delay_ = 1.0 / speed
        step_count = 0
        start_time = time.time() 
        
        while step_count < steps:    
            elapsed_time = time.time() - start_time
            
            if elapsed_time >= delay_:
                coils = coil_sequence[step_count%4]
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                start_time = time.time() 
                step_count += 1 

                if self.is_limit_switch_triggered(limit_switch_pin2) == 1 :
                    while self.is_limit_switch_triggered(limit_switch_pin2) == 1:
                        self.move_stepper_motor_backwards_nosafe(motor_id,steps = 10,speed=450)
                    return
                
                self.stepper_position[motor_id - 1] += 1
                if self.queue_button_start:
                    self.read_stepper_position()
            
    def move_stepper_motor_backwards(self, motor_id, steps, speed):
        """Fonction permettant de faire reculer le moteur pas-à-pas spécifié d'un certain nombre de pas à une vitesse donnée

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            steps (int): Nombre de pas à effectuer
            speed (int): Vitesse de déplacement du moteur
        """
        if speed > 525:
            speed = 525
            
        if motor_id == 1:
            limit_switch_pin1 = 1
        elif motor_id == 2:
            limit_switch_pin1 = 4
        elif motor_id == 3:
            limit_switch_pin1 = self.no_limit3
        
        coil_sequence = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 1, 1, 0), (1, 0, 1, 0)]
        delay_ = 1.0 / speed
        step_count = 0
        start_time = time.time() 

        while step_count < steps:  
            elapsed_time = time.time() - start_time
            if elapsed_time >= delay_:
                coils = coil_sequence[step_count%4]
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                start_time = time.time() 
                step_count += 1

                if self.is_limit_switch_triggered(limit_switch_pin1) == 1:
                    while self.is_limit_switch_triggered(limit_switch_pin1) == 1:
                        self.move_stepper_motor_forward_nosafe(motor_id,steps = 10,speed=450)
                    return
            
                self.stepper_position[motor_id - 1] -= 1
                if self.queue_button_start:
                    self.read_stepper_position()

    def move_stepper_motor_forward_nosafe(self, motor_id, steps, speed):
        """Fonction permettant de faire avancer le moteur pas-à-pas spécifié d'un certain nombre de pas à une vitesse donnée
        sans vérification des capteurs de fin de course

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            steps (int): Nombre de pas à effectuer
            speed (int): Vitesse de déplacement du moteur
        """
        if speed > 525:
            speed = 525
        
        coil_sequence = [(1, 0, 1, 0), (0, 1, 1, 0), (0, 1, 0, 1), (1, 0, 0, 1)]
        delay_ = 1.0 / speed
        step_count = 0
        start_time = time.time() 
        
        while step_count < steps:    
            elapsed_time = time.time() - start_time
            
            if elapsed_time >= delay_:
                coils = coil_sequence[step_count%4]
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                start_time = time.time() 
                step_count += 1 

    def move_stepper_motor_backwards_nosafe(self, motor_id, steps, speed):
        """Fonction permettant de faire reculer le moteur pas-à-pas spécifié d'un certain nombre de pas à une vitesse donnée
        sans vérification des capteurs de fin de course

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            steps (int): Nombre de pas à effectuer
            speed (int): Vitesse de déplacement du moteur
        """
        if speed > 525:
            speed = 525

        coil_sequence = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 1, 1, 0), (1, 0, 1, 0)]
        delay_ = 1.0 / speed
        step_count = 0
        start_time = time.time() 

        while step_count < steps:  
            elapsed_time = time.time() - start_time
            if elapsed_time >= delay_:
                coils = coil_sequence[step_count%4]
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                start_time = time.time() 
                step_count += 1

    def get_coil_pins(self, motor_id):
        """Fonction permettant de récupérer les numéros de broche des bobines pour le moteur spécifié

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)

        Returns:
            tuple: Numéros de broche des bobines du moteur spécifié.
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
        """Fonction permettant le déplacement du moteur pas-à-pas spécifié d'une distance spécifié,
        selon un certaine vitesse. Un déplacement positif fera avancer le moteur, tandis qu'un déplacement
        négatif le fera reculer.

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            distance (float): Distance à parcourir en millimètres
            speed (int): Vitesse de déplacement du moteur
        """
        degres_par_pas = 1.8  
        pas_par_mm = 0.125 

        pas = distance * pas_par_mm * (360 / degres_par_pas)
        pas_int = int(pas)

        if distance > 0:
            self.move_stepper_motor_forward(motor_id, pas_int, speed)
        elif distance < 0:
            self.move_stepper_motor_backwards(motor_id, abs(pas_int), speed)

    def laser_go_to_home(self):
        """Fonction permettant le déplacement du laser vers la position de calibration
        """
        motor_id = 1 
           
        self.move_stepper_motor_backwards(motor_id, steps=10000, speed=550)

        self.stepper_position[0] = 0

    def move_board_up(self):
        """Fonction permettant le déplacement du plateau vers le haut
        """
        motor_id = 2

        self.move_stepper_motor_backwards(motor_id, steps=10000, speed=300)

    def move_board_down(self):
        """Fonction permettant le déplacement du plateau vers le bas
        """
        motor_id = 2

        self.move_stepper_motor_forward(motor_id, steps=10000, speed=300)

    def move_board_to_pos(self):
        """Fonction permettant de bouger le plateau selon le rayon spécifié par l'interface au début du procédé
        """
        motor_id = 2
        diametre_verre = self.queue_radius
        hauteur = 150
        distance_focale = 25 
        position = (hauteur - distance_focale - diametre_verre)*-1

        self.move_stepper_to_distance(motor_id, position, 300)
   
    def gravure(self):
        """Fonction permettant d'effectuer la gravure. La séquence débute lors de la réception
        du message de début de l'interface, et se termine lorsque la position actuelle est
        plus grande que la position finale calculée
        """
        longueur_totale = 110
        position_initiale = 60

        self.move_stepper_to_distance(motor_id=1, distance=position_initiale, speed=450)
        self.stepper_position[0] = 0
        button_press = self.queue_button_start
        if button_press:
            sens = 1
            while self.stepper_position[2]*(pi*self.queue_radius/100) < self.queue_gravx:
                self.move_stepper_to_distance(motor_id=1, distance=longueur_totale*sens, speed=450)
                self.move_stepper_motor_forward(motor_id=3, steps=5, speed=350)
                sens *= -1
                time.sleep(0.25)

    def read_stepper_position(self):
        """Fonction permettant de lire les valeurs actuelles des moteurs et de les placer dans
        leur file synchronisé respective.
        """
        # if not hasattr(self, "sent_last_time"):
        #     self.sent_last_time = time.time()
        # if self.sent_last_time > time.time() + 50:
        #     stepper_position = (self.stepper_position[0]/0.125/(360/1.8))
        #     angle_position = self.stepper_position[2]*(pi*self.queue_radius/100)
        #     # self.queue_out.mutex.acquire()
        #     # ic([stepper_position, angle_position])
        #     self.queue_out.put([stepper_position, angle_position])
        #     # self.queue_out.mutex.release()
        #     self.sent_last_time = time.time()
        stepper_position = 110 - (self.stepper_position[0]/0.125/(360/1.8))
        angle_position = self.stepper_position[2]*(pi*self.queue_radius/100)
        res_y = self.laser_control.get(angle_position) or self.laser_control[min(self.laser_control.keys(), key = lambda key: abs(key-angle_position))]
        res_x = res_y.get(stepper_position) or res_y[min(res_y.keys(), key = lambda key: abs(key-stepper_position))]
        GPIO.output(self.LASER_pin, res_x)

    def sequence(self):
        """Fonction permettant l'exécution complète du programme
        """
        self.move_board_up()
        self.gravure()
        self.laser_go_to_home()
        self.move_board_down()
        self.queue_out.put("finis")
