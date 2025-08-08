import os
import can
from can_bus import CAN_Bus


TX = 0x100


def main():

	can0 = CAN_Bus(channel='can0',bitrate=500000)

	try:
		while True:

			received_msg = can0.receive_data(timeout=0.1)
			print("Received: ", received_msg)

			if received_msg is None:
				print('Timeout, no message')
	except KeyboardInterrupt:
		pass

	finally:
		can0.disable_can()

if __name__ == "__main__":
	main()
