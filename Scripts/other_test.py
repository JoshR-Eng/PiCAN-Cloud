from src.Cloud.cloudClient import Cloud
from src.PiCAN.can_handler import CAN_Handler
from src.DataHandling.can_buffer import CAN_buffer
from src.DataHandling.log import logger
import os 
import yaml
from dotenv import load_dotenv
from datetime import datetime, timezone

# =================================================================
# ------------------------- config import -------------------------
# =================================================================
load_dotenv()

with open('config.yaml', 'r') as yaml_config:
    config = yaml.safe_load(yaml_config)

# CAN Values
bitrate = config['can']['bitrate']
dbc_file_path = config['can']['dbc']

# Cloud Values
cloud_variables = config['cloud']['variables']
CloudURL = os.getenv('CloudURL')


# =================================================================
# -------------------------     setup     -------------------------
# =================================================================

# can
can0 = CAN_Handler(channel='can0', bitrate='bitrate', dbc_file=dbc_file_path)


# =================================================================
# -------------------------      loop     -------------------------
# =================================================================

def main():

    try:
        while True:
        
            received_frame = can0.receive_message(timeout=0.1)

            if received_frame:
                print(received_frame)
                
            else:
                print("ERROR: NO CAN Received")

    except KeyboardInterrupt:
        pass

    finally:
        can0.disable_can()

if __name__ == "__main__":
    main()
