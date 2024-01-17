from msvcrt import getch
from dynamixel_sdk import * 

class Moteurs:
    def __init__():
        # Control table address
        ADDR_PRO_TORQUE_ENABLE      = 64               
        ADDR_PRO_GOAL_POSITION      = 116
        ADDR_PRO_PRESENT_POSITION   = 132

        # Data Byte Length
        LEN_PRO_GOAL_POSITION       = 4
        LEN_PRO_PRESENT_POSITION    = 4

        # Protocol version
        PROTOCOL_VERSION            = 2.0               

        # Default setting
        DXL1_ID                     = 37                 # Dynamixel#1 ID : 1, moteur pour déplacement laser (axe y)
        DXL2_ID                     = 10                 # Dynamixel#2 ID : 2, moteur pour rotation verre (axe x)
        BAUDRATE                    = 57600              # Dynamixel default baudrate : 57600
        DEVICENAME                  = 'com6'             # Check which port is being used on your controller

        TORQUE_ENABLE               = 1                  # Value for enabling the torque
        TORQUE_DISABLE              = 0                  # Value for disabling the torque
        DXL_MINIMUM_POSITION_VALUE  = 100                # Dynamixel will rotate between this value
        DXL_MAXIMUM_POSITION_VALUE  = 4000               # and this value
        DXL_MOVING_STATUS_THRESHOLD = 20

        index = 0
        dxl_goal_position = [DXL_MINIMUM_POSITION_VALUE, DXL_MAXIMUM_POSITION_VALUE]         # Goal position


        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        portHandler = PortHandler(DEVICENAME)

        # Initialize PacketHandler instance
        # Set the protocol version
        # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
        packetHandler = PacketHandler(PROTOCOL_VERSION)

        # Initialize GroupSyncWrite instance
        groupSyncWrite = GroupSyncWrite(portHandler, packetHandler, ADDR_PRO_GOAL_POSITION, LEN_PRO_GOAL_POSITION)

        # Initialize GroupSyncRead instace for Present Position
        groupSyncRead = GroupSyncRead(portHandler, packetHandler, ADDR_PRO_PRESENT_POSITION, LEN_PRO_PRESENT_POSITION)

        # Open port
        if portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()

    def go_to_home(self,HOM_X,HOM_Z):
        while HOM_X == 1:
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, self.DXL1_ID, self.ADDR_PRO_TORQUE_ENABLE, self.TORQUE_ENABLE)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            else:
                print("Dynamixel#%d has been successfully connected" % self.DXL1_ID)

        print("Home")

    def gavure():
        print("Gravure")


monMoteur = Moteurs

monMoteur.go_to_home(monMoteur,1,1)
