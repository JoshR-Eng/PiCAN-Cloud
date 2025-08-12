import os
import can
from src.PiCAN.can_bus import CAN_Bus


TX = 0x200


def main():

	can0 = CAN_Bus(channel='can0',bitrate=500000)

	try:
		while True:

			received_msg = can0.receive_data(timeout=0.1)
			print("Received: ", received_msg)

			if received_msg is None:
				print('Timeout, no message')
			else:
				received_data = int.from_bytes(received_msg.data[0:2], 'little')
				print("received integer: ", received_data)

				data_to_send = received_data.to_bytes(2, 'little')
				can0.send_data(arb_id=TX, data=data_to_send)
				print("Sent back", data_to_send)
	except KeyboardInterrupt:
		pass

	finally:
		can0.disable_can()

if __name__ == "__main__":
	main()
