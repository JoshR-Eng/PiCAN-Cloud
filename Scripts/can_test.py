from can_bus import CAN_Bus
import time

TX_ID = 0x256

def main():
	can0 = CAN_Bus(channel="can0", bitrate=500000)

	try:
		while True:
			msg = can0.receive_data()
			if msg:
				print("\nReceived on can0")
			else:
				print("\n\t...")

			time.sleep(0.05)
	except KeyboardInterrupt:
		pass
	finally:
		can0.disable_can()

if __name__ == "__main__":
	main()
