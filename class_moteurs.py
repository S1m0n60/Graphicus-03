# Ajouter unité de vitesse fonction set_motor_speed
# Ajouter unité de distance fonction move_to_position

from queue import Queue
from dynamixel_sdk import * 
import RPi.GPIO as GPIO
from time import *

class Moteurs:
    def __init__(self):
        """Initialisation des paramètres pour le moteur Dynamixel XM430-W350-T
           Initialisation des E/S pour le Raspberry Pi
        """
        # Init moteur dynamixel
        ADDR_PRO_TORQUE_ENABLE      = 64               
        ADDR_PRO_GOAL_POSITION      = 116
        ADDR_PRO_PRESENT_POSITION   = 132
        LEN_PRO_GOAL_POSITION       = 4
        LEN_PRO_PRESENT_POSITION    = 4
        PROTOCOL_VERSION            = 2.0               
        motor_id                    = 10                 # Dynamixel#1 ID : 1, moteur pour rotation verre (axe x)
        BAUDRATE                    = 57600              # Dynamixel default baudrate : 57600
        DEVICENAME                  = 'com6'             # Check which port is being used on your controller
        TORQUE_ENABLE               = 1                  # Value for enabling the torque
        TORQUE_DISABLE              = 0                  # Value for disabling the torque
        DXL_MINIMUM_POSITION_VALUE  = 100                # Dynamixel will rotate between this value
        DXL_MAXIMUM_POSITION_VALUE  = 4000               # and this value
        DXL_MOVING_STATUS_THRESHOLD = 20
        dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]         # Goal position
        portHandler = PortHandler(DEVICENAME)
        packetHandler = PacketHandler(PROTOCOL_VERSION)
        groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION)
        groupSyncRead = GroupSyncRead(portHandler, packetHandler, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)

        # Init stepper
        self.enable_pin1, self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1 = 1, 2, 3, 4, 5
        self.enable_pin2, self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2 = 6, 7, 8, 9, 10
        self.enable_pin3, self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3 = 11, 12, 13, 14, 15  # A remplacer avec les vrais PINS -----------------

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup([self.enable_pin1, self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup([self.enable_pin2, self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2], GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup([self.enable_pin3, self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3], GPIO.OUT, initial=GPIO.LOW)


        self.limit_switch_pins = [16, 17, 18, 19]  # A remplacer avec les vrais PINS -----------------
        GPIO.setup(self.limit_switch_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        self.stepper_position = 0
        self.MAX_STEP_DIFFERENCE = 2

    def is_limit_switch_triggered(self, switch_id):
        """Fonction pour vérifier si un des capteurs de fin de course est activé

        Args:
            switch_id (int): Numéro d'identification du capteur de fin de course (1-4)

        Returns:
            int: 0 - Capteur de fin de course non-actif
                 1 - capteur de fin de course actif
        """
        return not GPIO.input(self.limit_switch_pins[switch_id-1])

    def disable_torque(self):
        """Fonction permettant de désactiver le couple du moteur Dynamixel
           Cette fonction peut être utilisé pour arrêter le moteur
        """
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.motor_id, self.ADDR_PRO_TORQUE_ENABLE, self.TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication error while disabling torque, error: {dxl_comm_result}, {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Error while disabling torque, error: {dxl_error}")
        else:
            print("Torque disabled successfully")

    def enable_torque(self):
        """Fonction permettant d'activer le couple du moteur Dynamixel
           Cette fonction doit être utilisé avant tout autre fonction de mouvement
        """
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL1_ID, self.ADDR_PRO_TORQUE_ENABLE, self.TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication error while enabling torque, error: {dxl_comm_result}, {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Error while enabling torque, error: {dxl_error}")
        else:
            print("Torque enabled successfully")

    def set_motor_speed(self, speed):
        """Fonction permettant de faire avancer le moteur Dynamixel selon une vitesse spécifiée

        Args:
            speed (int): Vitesse désirée du moteur en ???
        """
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, self.motor_id, self.ADDR_PRO_GOAL_POSITION, speed)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication error while setting speed, error: {dxl_comm_result}, {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Error while setting speed, error: {dxl_error}")
        else:
            print(f"Speed of motor {self.motor_id} set successfully to {speed}")

    def move_to_position(self,target_position):
        """Fonction permettant de faire avancer le moteur Dynamixel selon une position désirée

        Args:
            target_position (float): Position désirée du moteur en ???
        """
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, self.motor_id, self.ADDR_PRO_GOAL_POSITION, target_position)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication error during movement, error: {dxl_comm_result}, {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Error during movement, error: {dxl_error}")
        else:
            print(f"Motor {self.motor_id} moved successfully to position {target_position}")

    def move_dynamixel_angle(self, angle_value):
        """Fonction permettant de faire tourner le moteur Dynamixel selon une valeur d'angle désirée

        Args:
            angle_value (float): Rotation désirée du moteur en degrés
        """
        current_position = self.read_motor_state(self.motor_id)
        new_position = current_position + angle_value

        if new_position > self.DXL_MAXIMUM_POSITION_VALUE:
            new_position = self.DXL_MINIMUM_POSITION_VALUE + (new_position - self.DXL_MAXIMUM_POSITION_VALUE)

        self.move_to_position(self.motor_id, new_position)

    def read_motor_state(self):
        """Fonction pour lire la position actuelle du moteur Dynamixel

        Returns:
            float: Position actuelle du moteur en ???
        """
        dxl_present_position, _, _, _ = self.packetHandler.read4ByteTxRx(self.portHandler, self.motor_id, self.ADDR_PRO_PRESENT_POSITION)
        return dxl_present_position
    
    def read_torque_status(self):
        """Fonction permettant de savoir si le couple du moteur Dynamixel est actif ou inactif

        Returns:
            int: 0 - Couple du moteur inactif
                 1 - Couple du moteur actif
        """
        dxl_torque_enable, _, _, _ = self.packetHandler.read1ByteTxRx(self.portHandler, self.motor_id, self.ADDR_PRO_TORQUE_ENABLE)
        return dxl_torque_enable
    
    def read_motor_speed(self):
        """Fonction permettant de savoir la vitesse actuelle du moteur Dynamixel

        Returns:
            float: Vitesse actuelle du moteur en ???
        """
        dxl_speed, _, _, _ = self.packetHandler.read2ByteTxRx(self.portHandler, self.motor_id, self.ADDR_PRO_PRESENT_POSITION)
        return dxl_speed
    
    def enable_stepper_motor(self, motor_id):
        """Fonction permettant d'activer un des moteurs pas-à-pas

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
        """
        enable_pin = self.get_enable_pin(motor_id)
        GPIO.output(enable_pin, GPIO.HIGH)
        print(f"Stepper Motor {motor_id} enabled.")

    def disable_stepper_motor(self, motor_id):
        """Fonction permettant de désactiver un des moteurs pas-à-pas

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
        """
        enable_pin = self.get_enable_pin(motor_id)
        GPIO.output(enable_pin, GPIO.LOW)
        print(f"Stepper Motor {motor_id} disabled.")

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
            speed (float): Vitesse du moteur désirée en ???
        """
        if motor_id == 1:
            coil_sequence = [(1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 1), (1, 0, 0, 1)]
        elif motor_id == 2:
            coil_sequence = [(1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 1), (1, 0, 0, 1)]
        elif motor_id == 3:
            coil_sequence = [(1, 1, 0, 0), (0, 1, 1, 0), (0, 0, 1, 1), (1, 0, 0, 1)]
        else:
            print(f"Invalid motor_id: {motor_id}")
            return

        delay = 1.0 / speed

        for _ in range(steps):
            for coils in coil_sequence:
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                sleep(delay)

            self.stepper_position += 1

    def move_stepper_motor_backwards(self, motor_id, steps, speed):
        """Fonction permettant de faire reculer un moteur pas-à-pas selon une vitesse et un nombre de pas spécifié

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            steps (int): Nombre de pas désiré
            speed (float): Vitesse du moteur désirée en ???
        """
        if motor_id == 1:
            coil_sequence = [(1, 0, 0, 1), (0, 0, 1, 1), (0, 1, 1, 0), (1, 1, 0, 0)]
        elif motor_id == 2:
            coil_sequence = [(1, 0, 0, 1), (0, 0, 1, 1), (0, 1, 1, 0), (1, 1, 0, 0)]
        elif motor_id == 3:
            coil_sequence = [(1, 0, 0, 1), (0, 0, 1, 1), (0, 1, 1, 0), (1, 1, 0, 0)]
        else:
            print(f"Invalid motor_id: {motor_id}")
            return

        delay = 1.0 / speed

        for _ in range(steps):
            for coils in coil_sequence:
                for coil_pin, coil_state in zip(self.get_coil_pins(motor_id), coils):
                    GPIO.output(coil_pin, GPIO.HIGH if coil_state else GPIO.LOW)
                sleep(delay)

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
        """Fonction permettant de bouger le moteur pas-à-pas selon une distance spécifiée

        Args:
            motor_id (int): Identifiant du moteur pas-à-pas (1-3)
            distance (float): Distance spécifiée en mm 
            speed (float): Vitesse du moteur désirée en ???
        """
        # Specs
        step_angle = 1.8
        steps_per_revolution = 200

        # 2mm entre chaque tour pour la vis sans fin
        kg = 2

        # Distance par revolution
        pitch = 360 / (step_angle * steps_per_revolution * kg)

        # NB de pas pour distance voulue
        steps = int(distance / pitch)

        if steps < 0 :
            self.move_stepper_motor_backwards(motor_id, steps, speed)
        else:
            self.move_stepper_motor_forward(motor_id, steps, speed)

        

    def laser_go_to_home(self):
        """Fonction permettant le déplacement du moteur Dynamixel jusqu'à l'activation d'un des 2 capteurs de fin de course
        """
        motor_id = 1 
        self.enable_stepper_motor(motor_id)
        
        limit_switch_id = motor_id
        limit_switch_id2 = motor_id + 1
        limit_switch_pin = self.limit_switch_pins[limit_switch_id - 1]
        limit_switch_pin2 = self.limit_switch_pins[limit_switch_id2 - 1]
        
        while not (self.is_limit_switch_triggered(limit_switch_pin) or self.is_limit_switch_triggered(limit_switch_pin2)):
            self.move_stepper_motor_forward(motor_id, steps=1, speed=10)

        self.stepper_position = 0
        self.disable_stepper_motor(motor_id)
        print(f"Laser stepper motor at home position.")

    def move_board_up(self):
        """Fonction permettant de bouger les moteurs 2 et 3 pas-à-pas en même temps pour faire bouger la plateforme vers le haut
        """
        motors = [2, 3]
        limit_switch_id1 = 3
        limit_switch_id2 = 4

        limit_switch_pin1 = self.limit_switch_pins[limit_switch_id1 - 1]
        limit_switch_pin2 = self.limit_switch_pins[limit_switch_id2 - 1]

        for motor_id in motors:
            self.enable_stepper_motor(motor_id)

        steps_taken = {motor_id: 0 for motor_id in motors}

        while not (self.is_limit_switch_triggered(limit_switch_pin1) or self.is_limit_switch_triggered(limit_switch_pin2)):
            for motor_id in motors:
                steps = self.move_stepper_motor_forward(motor_id, steps=1, speed=10)
                steps_taken[motor_id] += steps

            if abs(steps_taken[2] - steps_taken[3]) > self.MAX_STEP_DIFFERENCE:
                ahead_motor = 2 if steps_taken[2] > steps_taken[3] else 3
                behind_motor = 3 if steps_taken[2] > steps_taken[3] else 2
                steps_to_wait = abs(steps_taken[ahead_motor] - steps_taken[behind_motor])
                for _ in range(steps_to_wait):
                    self.move_stepper_motor_forward(behind_motor, steps=1, speed=10)

        for motor_id in motors:
            self.disable_stepper_motor(motor_id)

    def move_board_down(self):
        """Fonction permettant de bouger les moteurs 2 et 3 pas-à-pas en même temps pour faire bouger la plateforme vers le bas
        """
        motors = [2, 3]
        limit_switch_id1 = 3
        limit_switch_id2 = 4

        limit_switch_pin1 = self.limit_switch_pins[limit_switch_id1 - 1]
        limit_switch_pin2 = self.limit_switch_pins[limit_switch_id2 - 1]

        for motor_id in motors:
            self.enable_stepper_motor(motor_id)

        steps_taken = {motor_id: 0 for motor_id in motors}

        while not (self.is_limit_switch_triggered(limit_switch_pin1) or self.is_limit_switch_triggered(limit_switch_pin2)):
            for motor_id in motors:
                steps = self.move_stepper_motor_backwards(motor_id, steps=1, speed=10)
                steps_taken[motor_id] += steps

            if abs(steps_taken[2] - steps_taken[3]) > self.MAX_STEP_DIFFERENCE:
                ahead_motor = 2 if steps_taken[2] > steps_taken[3] else 3
                behind_motor = 3 if steps_taken[2] > steps_taken[3] else 2
                steps_to_wait = abs(steps_taken[ahead_motor] - steps_taken[behind_motor])
                for _ in range(steps_to_wait):
                    self.move_stepper_motor_backwards(behind_motor, steps=1, speed=10)

        for motor_id in motors:
            self.disable_stepper_motor(motor_id)
    
    def read_stepper_position(self):
        """Fonction permettant de retourner le nombre de pas effectué par le moteur pas-à-pas

        Returns:
            int: Nombre de pas effectué
        """
        stepper_position_queue = Queue()
        return stepper_position_queue.put(self.stepper_position)
    
    def gravure(self, total_length, glass_length, grav_start, dynamixel_angle_interval, num_round_trips, speed):
        """Fonction permettant d'effectuer la séquence de gravure des verres

        Args:
            total_length (float): Longueur totale du mouvement possible du moteur Dynamixel en cm
            glass_length (float): Longueur totale du verre en cm
            grav_start (float): Distance entre le bord du verre et le début de la gravure en cm
            dynamixel_angle_interval (int): Angle voulue entre les passes de gravure en degrés
            num_round_trips (int): Nombre d'allers-retours voulues
            speed (int): Vitesse de gravure voulue en ???
        """
        stepper_positions_queue = Queue()
        dynamixel_positions_queue = Queue()

        point_a = total_length - glass_length + grav_start
        point_b = point_a + glass_length

        for _ in range(num_round_trips):
            self.move_stepper_to_distance(1, point_b, speed, kg = 1)

            stepper_positions_queue.put(self.read_stepper_position())
            dynamixel_positions_queue.put(self.read_motor_state())

            dynamixel_target_angle = self.read_motor_state() + dynamixel_angle_interval
            self.move_dynamixel_angle(1, dynamixel_target_angle)

            self.move_stepper_to_distance(1, point_a, speed, kg = 1)

            stepper_positions_queue.put(self.read_stepper_position())
            dynamixel_positions_queue.put(self.read_motor_state())

            dynamixel_target_angle = self.read_motor_state() + dynamixel_angle_interval
            self.move_dynamixel_angle(1, dynamixel_target_angle)

    def read_values(self):
        """Function pour lire les positions en x et y

        Returns:
            tuple: Un tuple contenant les positions en x et y
                x (float): Angle lu par le moteur Dynamixel
                y (float): Valeur de distance lue par le moteur pas-à-pas
        """
        x = self.read_motor_state()

        step_angle = 1.8  
        steps_per_revolution = 200
        screw_pitch = 2 
        steps_per_mm = steps_per_revolution / (360 / step_angle) / screw_pitch
        y_distance_mm = self.stepper_position / steps_per_mm

        return x, y_distance_mm


testmoteur = Moteurs()
testmoteur.enable_stepper_motor(1)
testmoteur.enable_stepper_motor(4)
testmoteur.move_stepper_motor_forward(4,1,10)
testmoteur.move_stepper_motor_forward(1,1,10)
testmoteur.move_stepper_motor_backwards(1,1,10)
print(testmoteur.is_limit_switch_triggered(2))
testmoteur.set_motor_speed(10)
testmoteur.read_motor_state()
testmoteur.read_stepper_position()
testmoteur.enable_torque()
testmoteur.move_dynamixel_angle(12)
testmoteur.move_to_position(30)
testmoteur.disable_stepper_motor(1)
testmoteur.disable_stepper_motor(4)

