"""
ADD FILE DESCRIPTION
"""

# =================================================================
#  -------------------------  pkg imports  ------------------------
# =================================================================

from src.Cloud.cloudClient import Cloud
from src.PiCAN.can_handler import CAN_Handler
from src.DataHandling.log import logger
import os 
import yaml
from dotenv import load_dotenv
from time import sleep, time

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
cloud_return_variables = config['cloud']['cloud_return_variables']
cloud_warmup_period = config['cloud']['warmup_period']
cloud_warmup_counter = 0
CloudURL = os.getenv('CloudURL')

# Globally define inital values for RLS
covariance = config['rls']['covariance']
time_prev = None
temp_prev = None


# =================================================================
# -------------------------     setup     -------------------------
# =================================================================

can0 = CAN_Handler(channel='can0', bitrate=bitrate, dbc_file=dbc_file_path)

cloud = Cloud(URL=CloudURL, timeout=3, return_variables=cloud_return_variables)

log_header = cloud_return_variables + ['time_recv','current','dt']
log = logger(directory_path='Logs/', file_headers=log_header)

print(f"Main function will begin now,\nDT will warmup with" \
    f" [{cloud_warmup_period}] Iterations")
# =================================================================
# -------------------------      loop     -------------------------
# =================================================================

def main():

    global internal_resistance, covariance, time_prev, temp_prev, cloud_warmup_counter

    try:
        while True:
        
            received_frame = can0.receive_message(timeout=0.1)

            if received_frame:
                

                temp = received_frame.get('Battery_Temperature')
                current = received_frame.get('Battery_Current')
                internal_resistance = received_frame.get('Battery_Internal_Resistance')
                cooling_power = received_frame.get('BTM_Power')

                print(f"\nRECEIVED"\
                      f"\n\tT: {temp}\n\tI: {current}\n\tRbat: {internal_resistance}\n\t"\
                      f"Pbtm: {cooling_power}")

                if temp_prev is None or time_prev is None:
                    temp_prev = temp
                    time_prev = time()
                    sleep(0.1)
                    continue

                if abs(current) < 5:
                    sleep(1)
                    continue # Low amps produce unreliable values and noise so skip
                
                time_sent = time()          # Remeber to assign this to time_prev after
                dt = time_sent - time_prev
                
                payload = {
                    'time_sent': time_sent,
                    'temp': temp,
                    'temp_prev': temp_prev,
                    'current': current,
                    'cooling_power': cooling_power,
                    'dt': dt,
                    'internal_resistance': internal_resistance,
                    'p': covariance,
                }

                cloud_response = cloud.send_dataset(payload=payload)

                if cloud_response:
                    print("Cloud Responded")
                    if cloud_warmup_counter < cloud_warmup_period:  # A warmup period for Cloud controller
                        if cloud_warmup_counter == cloud_warmup_period -2:
                            print("\n\n\n\t -------- Warmup Complete. Going Live... -------- \n\n\n")
                        cloud_warmup_counter += 1
                        sleep(1)
                        continue
                    else:
                        internal_resistance = float(
                            "{:.5f}".format(cloud_response['internal_resistance']))

                        can_payload = {'RPiBattery_Internal_Resistance': internal_resistance}
                        can0.send_message(signals=can_payload, message_name='RPi')
                        print(f"RETURNED\n\t {can_payload}")

                    covariance = cloud_response['p']
                    time_prev = time_sent
                    temp_prev = temp

                    data_to_log = cloud_response
                    data_to_log['current'] = current
                    data_to_log['dt'] = dt
                    
                    log.append(data_to_log)
                else:
                    print("ERROR: No response from cloud") 
                    time_prev = time_sent # make sure values are still updated
                    temp_prev = temp
            else:
                print("ERROR: NO CAN Received")
                
            sleep(1)
            
            
    except KeyboardInterrupt:
        pass
    finally:
        can0.disable_can()

if __name__ == "__main__":
    main()
