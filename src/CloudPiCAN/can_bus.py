import can
import os

class CAN_Bus:
    
    """
    This class defines a CAN Bus Object 
    Inputs = CAN channel, bitrate
    Methods = send_data, recieve_data, disable_can
    """

    def __init__(self, channel: str, bitrate: int):
    
        valid_channels = ("can0", "can1")
        if channel not in valid_channels:
            raise ValueError(
                f"Error, Invalid channel '{channel}'\nMust be one of the following:\n\tcan0\n\tcan1"
            )
        
        self.channel = channel
        self.bitrate = bitrate
        self.bus = self.setup_bus()


    def setup_bus(self):
        os.system(f'sudo ip link set {self.channel} type can bitrate {self.bitrate}')
        os.system(f'sudo ifconfig {self.channel} up')
        return can.interface.Bus(channel=self.channel, interface='socketcan')
    

    def send_message(self, arb_id: int, data: bytes):
        msg = can.Message(arbitration_id=arb_id,
                          data=list(data),
                          is_extended_id=False)
        try:
            self.bus.send(msg)
            print("Sent:", msg)                     
        except can.CanError as e:
            print(f'Send Error [CAN]: {e}')

    
    def receive_message(self, arb_id: int, timeout: float = 0.1) -> can.Message:
        try:
            msg = self.bus.recv(timeout)
            if msg.arbiration_id == arb_id:
                # physical value = (raw value * factor +offset) * unit of measurement
                received = {
                    'raw_frame': msg.data,
                    'pi_receive_time': msg.timestamp
                    }
                return received
            else: 
                print("ERROR: Specified arbiration ID didn't match CAN data")
        except can.CanError as e:
            print(f'Receive Error [CAN]: {e}')
            return None
        

    def disable_can(self):
        self.bus.shutdown()
        os.system(f'sudo ifconfig {self.channel} down')
