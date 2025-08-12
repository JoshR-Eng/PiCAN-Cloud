import requests
from datetime import timezone, datetime

class Cloud:

    def __init__(self, URL:str, timeout:int=1):
        if not URL:
            raise TypeError("Provide a URL to Cloud Service")
        self.URL = URL

    def send_dataset(self, payload):
        try:
            response = requests.post(self.URL, json=payload)
            client_recieve_time = datetime.now(timezone.utc)

            if response.status_code == 200:
                cloud_return = response.json()
                returned_value = cloud_return.get('response_variable')
                client_send_time = cloud_return.get('client_send_time')
                feedback = {
                    'response_variable': returned_value,
                    'client_send_time': client_send_time,
                    'client_recieve_time': client_recieve_time
                }
                return feedback
            else:
                print(f"ERROR: Cloud Status Code {response.status_code} ")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Network Connection failed\n{e}")
            return None

