from src.PiCAN.can_bus import CAN_Bus
from src.PiCAN.can_message import Signal
from time import sleep


RX = 200
Temperature_Signal = Signal(length=2, start_byte=0, factor=0.01, offset=0)

def main():

    can0 = CAN_Bus(channel='can0', bitrate=500000)

    try:
        while True:
        
            received_frame = can0.receive_message(RX, timeout=0.1) 
            temperature = Temperature_Signal.decode(received_frame['raw_frame'])
            print(f"Received the value: {temperature}")

            sleep(3)
    except KeyboardInterrupt:
        pass

    finally:
        can0.disable_can()

if __name__ == "__main__":
    main()
