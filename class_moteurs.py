from msvcrt import getch
from dynamixel_sdk import * 
import RPi.GPIO as GPIO
from time import *

class Moteurs:
    def __init__(self):
        # Init moteur dynamixel
        ADDR_PRO_TORQUE_ENABLE      = 64               
        ADDR_PRO_GOAL_POSITION      = 116
        ADDR_PRO_PRESENT_POSITION   = 132
        LEN_PRO_GOAL_POSITION       = 4
        LEN_PRO_PRESENT_POSITION    = 4
        PROTOCOL_VERSION            = 2.0               
        DXL1_ID                     = 10                 # Dynamixel#1 ID : 1, moteur pour rotation verre (axe x)
        BAUDRATE                    = 57600              # Dynamixel default baudrate : 57600
        DEVICENAME                  = 'com6'             # Check which port is being used on your controller
        TORQUE_ENABLE               = 1                  # Value for enabling the torque
        TORQUE_DISABLE              = 0                  # Value for disabling the torque
        DXL_MINIMUM_POSITION_VALUE  = 100                # Dynamixel will rotate between this value
        DXL_MAXIMUM_POSITION_VALUE  = 4000               # and this value
        DXL_MOVING_STATUS_THRESHOLD = 20
        index = 0
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

    def is_limit_switch_triggered(self, switch_id):
        # Fonction pour verifier l'etat des limit switch
        return not GPIO.input(self.limit_switch_pins[switch_id])

    def disable_torque(self):
        # Function to disable the torque of the Dynamixel motor
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL1_ID, self.ADDR_PRO_TORQUE_ENABLE, self.TORQUE_DISABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication error while disabling torque, error: {dxl_comm_result}, {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Error while disabling torque, error: {dxl_error}")
        else:
            print("Torque disabled successfully")

    def enable_torque(self):
        # Function to enable torque for the Dynamixel motor
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL1_ID, self.ADDR_PRO_TORQUE_ENABLE, self.TORQUE_ENABLE)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication error while enabling torque, error: {dxl_comm_result}, {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Error while enabling torque, error: {dxl_error}")
        else:
            print("Torque enabled successfully")

    def set_motor_speed(self, motor_id, speed):
        # Function to set the speed of the Dynamixel motor
        dxl_comm_result, dxl_error = self.packetHandler.write2ByteTxRx(self.portHandler, motor_id, self.ADDR_PRO_GOAL_POSITION, speed)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication error while setting speed, error: {dxl_comm_result}, {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Error while setting speed, error: {dxl_error}")
        else:
            print(f"Speed of motor {motor_id} set successfully to {speed}")

    def move_to_position(self, motor_id, target_position):
        # Function to set a target position for the Dynamixel motor
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(self.portHandler, motor_id, self.ADDR_PRO_GOAL_POSITION, target_position)
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication error during movement, error: {dxl_comm_result}, {self.packetHandler.getTxRxResult(dxl_comm_result)}")
        elif dxl_error != 0:
            print(f"Error during movement, error: {dxl_error}")
        else:
            print(f"Motor {motor_id} moved successfully to position {target_position}")


    def read_motor_state(self, motor_id):
        # Fonction pour lire les valeurs renvoyes par le moteur Dynamixel
        dxl_present_position, _, _, _ = self.packetHandler.read4ByteTxRx(self.portHandler, motor_id, self.ADDR_PRO_PRESENT_POSITION)
        return dxl_present_position
    
    def read_torque_status(self, motor_id):
        dxl_torque_enable, _, _, _ = self.packetHandler.read1ByteTxRx(self.portHandler, motor_id, self.ADDR_PRO_TORQUE_ENABLE)
        return dxl_torque_enable
    
    def read_motor_speed(self, motor_id):
        dxl_speed, _, _, _ = self.packetHandler.read2ByteTxRx(self.portHandler, motor_id, self.ADDR_PRO_PRESENT_POSITION)
        return dxl_speed
    
    def enable_stepper_motor(self, motor_id):
        # Function to enable the specified stepper motor
        enable_pin = self.get_enable_pin(motor_id)
        GPIO.output(enable_pin, GPIO.HIGH)
        print(f"Stepper Motor {motor_id} enabled.")

    def disable_stepper_motor(self, motor_id):
        # Function to disable the specified stepper motor
        enable_pin = self.get_enable_pin(motor_id)
        GPIO.output(enable_pin, GPIO.LOW)
        print(f"Stepper Motor {motor_id} disabled.")

    def get_enable_pin(self, motor_id):
        # Function to get the enable pin based on the motor_id
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


    def get_coil_pins(self, motor_id):
        if motor_id == 1:
            return (self.coil_A1, self.coil_B1, self.coil_C1, self.coil_D1)
        elif motor_id == 2:
            return (self.coil_A2, self.coil_B2, self.coil_C2, self.coil_D2)
        elif motor_id == 3:
            return (self.coil_A3, self.coil_B3, self.coil_C3, self.coil_D3)
        else:
            return ()
        

    def laser_go_to_home(self):
        motor_id = 1 
        self.enable_stepper_motor(motor_id)
        
        limit_switch_id = motor_id
        limit_switch_id2 = motor_id + 1
        limit_switch_pin = self.limit_switch_pins[limit_switch_id - 1]
        limit_switch_pin2 = self.limit_switch_pins[limit_switch_id2 - 1]
        
        while not (self.is_limit_switch_triggered(limit_switch_pin) or self.is_limit_switch_triggered(limit_switch_pin2)):
            self.move_stepper_motor_forward(motor_id, steps=1, speed=10)

        self.disable_stepper_motor(motor_id)
        print(f"Laser stepper motor at home position.")

    def move_board(self, steps, speed):
        motors = [2, 3]
        limit_switch_id1 = 3
        limit_switch_id2 = 4

        limit_switch_pin1 = self.limit_switch_pins[limit_switch_id1 - 1]
        limit_switch_pin2 = self.limit_switch_pins[limit_switch_id2 - 1]

        for motor_id in motors:
            self.enable_stepper_motor(motor_id)

        while not (self.is_limit_switch_triggered(limit_switch_pin1) or self.is_limit_switch_triggered(limit_switch_pin2)):
            for motor_id in motors:
                self.move_stepper_motor_forward(motor_id, steps, speed)

        for motor_id in motors:
            self.disable_stepper_motor(motor_id)

        print("Stepper Motors 2 and 3 moved together.")

    

    