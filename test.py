import os
import can

os.system('sudo ip link set can0 type can bitrate 100000')
os.system('sudo ip link set can1 type can bitrate 100000')
os.system('sudo ifconfig can0 up')
os.system('sudo ifconfig can1 up')

can0 = can.interface.Bus(channel='can0', interface='socketcan')
can1 = can.interface.Bus(channel='can1', interface='socketcan')

try:
	msg = can.Message( is_extended_id=False, arbitration_id=0x123, data = [0,1,2,3,4,5,6,7])
	
	can1.send(msg)
	print("sent: ", msg)

	received_msg = can0.recv(0.1)
	print("recieved: ", received_msg)

	if received_msg is None:
		print('Timout, no message')

finally:
	can0.shutdown()
	can1.shutdown()

	os.system('sudo ifconfig can0 down')
	os.system('sudo ifconfig can1 down')
