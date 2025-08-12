import can

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
        raw_signal_int = (physical_value - self.offset) / self.factor

        if self.is_little_endian:
            raw_signal_data = int.to_bytes(raw_signal_int, 'little')
        else:
            raw_signal_data = int.to_bytes(raw_signal_int, 'big')
        
        return raw_signal_data

