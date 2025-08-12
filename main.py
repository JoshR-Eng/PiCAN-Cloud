"""
ADD FILE DESCRIPTION
"""

# =================================================================
#  -------------------------  pkg imports  ------------------------
# =================================================================

from src.Cloud.cloudClient import Cloud
from src.PiCAN.can_bus import CAN_Bus
from src.PiCAN.can_message import Signal
from src.DataHandling.CAN_buffer import CAN_buffer
from src.DataHandling.log import logger
import os 
import yaml
from dotenv import load_dotenv

# =================================================================
# ------------------------- config import -------------------------
# =================================================================
with open('config.yaml', 'r') as yaml_config:
    config = yaml.safe_load(yaml_config)

# CAN Values
RX = config['can']['RX']
TX = config['can']['TX']
bitrate = config['can']['bitrate']

# Cloud Values
cloud_variables = config['cloud']['variables']
CloudURL = os.getenv('CloudURL')


# =================================================================
# -------------------------     setup     -------------------------
# =================================================================

# can
can0 = CAN_Bus(channel='can0', bitrate=bitrate)
Rx_temperature_signal = Signal(length=2, start_byte=0, factor=0.01, offset=0)
Tx_cooling_power_signal = Signal(length=2, start_byte=0, factor=0.01, offset=0)

# cloud
cloud = Cloud(URL=CloudURL, timeout=1, return_variables=cloud_variables)

# log
log_header = cloud_variables + ['client_recieve_time']
log = logger(file_path='Logs/', file_headers=log_header)


# =================================================================
# -------------------------      loop     -------------------------
# =================================================================

def main():

    try:
        while True:
        
            received_frame = can0.receive_message(RX, timeout=0.1) 

            if received_frame is not None:
                temperature = Rx_temperature_signal.decode(received_frame['raw_frame'])
                print(f"Received the value: {temperature:.2f}")

                # Send payload to the cloud
                payload = {
                    "temperature": temperature,
                    "dt": 0.5,
                    "client_send_time": received_frame['pi_receive_time']
                }
                cloud_response = cloud.send_dataset(payload=payload)

                # Check response is valid
                if cloud_response and 'cooling_power' in cloud_response:
                    cooling_power = float("{:.2f}".format(cloud_response['cooling_power']))
                    print(f"Cloud returned cooling power: {cooling_power}")

                    # Send command to dSPACE
                    encoded_cooling_power = Tx_cooling_power_signal.encode(cooling_power)
                    can0.send_message(arb_id=TX, data=encoded_cooling_power)
                    print(f"\n\tCAN TX message sent to dSPACE")

                    # Log Data
                    log.append(cloud_response)

            else:
                print("\nNo message Received")

    except KeyboardInterrupt:
        pass

    finally:
        can0.disable_can()

if __name__ == "__main__":
    main()
