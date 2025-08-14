import can
import cantools
import os

class CAN_Handler:
    """
    Higher level CAN handler that uses DBC file to 
    automatically encode/decode messages and their signals
    """

    def __init__(self, channel: str, bitrate: int, dbc_file: str):
        valid_channels = ("can0", "can1")
        if channel not in valid_channels:
            raise ValueError(
                f"Error, Invalid channel: '{channel}'\nMust be one of the following:\n\tcan0\n\tcan1"
            )
        try:
            self.dbc = cantools.database.load_file(dbc_file)
            print(f"DBC file loaded successfully")
        except FileNotFoundError:
            print(f"ERROR: DBC file not found at '{dbc_file}")
            raise

        self.channel = channel
        self.bitrate = bitrate
        try:
            self.bus = self.setup_bus()
            print(f"{channel} Initialised\n\tbitrate: {bitrate}\n\tDBC File: {dbc_file}")
        except Exception as e:
            print(f"ERROR: Failed to initalise CAN: {e}")
            raise


    def setup_bus(self):
        os.system(f'sudo ip link set {self.channel} type can bitrate {self.bitrate}')
        os.system(f'sudo ifconfig {self.channel} up')
        return can.interface.Bus(channel=self.channel, interface='socketcan')
    

    def send_message(self, signals: dict, message_name:str='RPi'):
        try:
            msg = self.dbc.get_message_by_name(message_name)
            data = msg.encode(signals)
            can_message = can.Message(arbitration_id=msg.frame_id,
                                      data=data,
                                      is_extended_id=False)
            self.bus.send(can_message)
        except Exception as e:
            print(f"ERROR: Failed to send message\n\t{e}")

    
    def receive_message(self, timeout: float = 0.1):
        try:
            msg = self.bus.recv(timeout)
            if msg:
                try:
                    received = self.dbc.decode_message(msg.arbitration_id, msg.data)
                    return received
                except KeyError:
                    print(f"INFO: Received message with non-matching ID: {msg.arbitration_id}")
                    return None
            else:
                print("INFO: No message received within timeout period")
                return None
        except can.CanError as e:
            print(f'ERROR: tried to receive CAN message {e}')
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
    