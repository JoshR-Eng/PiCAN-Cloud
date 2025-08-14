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
            print(f'ERROR: Can {e}')

    
    def receive_message(self, arb_id: int, timeout: float = 0.1):
        """ Returns a dictionary containting 'raw_frame' and 'pi_receive_time' """
        try:
            msg = self.bus.recv(timeout)
            if msg is not None:
                if msg.arbitration_id == arb_id:
                    received = {
                        'raw_frame': msg.data,
                        'pi_receive_time': msg.timestamp
                    }
                    return received
                else:
                    print(f"INFO: Received message with non-matching ID: {msg.arbitration_id}")
            else:
                print("INFO: No message received within timeout period")
                return None
        except can.CanError as e:
            print(f'Receive Error [CAN]: {e}')
            return None
        

    def disable_can(self):
        self.bus.shutdown()
        os.system(f'sudo ifconfig {self.channel} down')

    
    def flush_rx(self):
        while True:
            msg = self.bus.recv(timeout=0.1)
            if msg is None:
                break
        return None
    



class Signal: 
    """
    A that defines the signal in a CAN message
    It can extract the signal from a larger CAN message 
    or it can just encode the signal into a byte array - it'll need to be order after
    """

    def __init__(self, length:int, start_byte:int=0, factor:float=0, offset:float=0, is_little_endian=True):
        self.length = length        # This is in number of bytes
        self.start_byte = start_byte
        self.factor = factor
        self.offset = offset
        self.is_little_endian = is_little_endian


    def decode(self, raw_frame_data: bytearray) -> float:
        """ Takes the raw data and outputs the physical value"""
        raw_signal_data = raw_frame_data[self.start_byte:(self.start_byte + self.length)]
        if self.is_little_endian:
            raw_signal_int = int.from_bytes(raw_signal_data, 'little')
        else:
            raw_signal_int = int.from_bytes(raw_signal_data, 'big')

        physical_value = (raw_signal_int * self.factor) + self.offset
        return physical_value


    def encode(self, physical_value: float) -> bytearray:
        """ Takes physical value and outputs it in a string of bytes"""
        raw_signal_int = int((physical_value - self.offset) / self.factor)

        if self.is_little_endian:
            raw_signal_data = raw_signal_int.to_bytes(self.length, 'little')
        else:
            raw_signal_data = raw_signal_int.to_bytes(self.length, 'big')
        
        return raw_signal_data