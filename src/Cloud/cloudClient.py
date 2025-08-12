import requests
from datetime import timezone, datetime

class Cloud:
    """
    This class defines the cloud

    argv:
        URL              (str)  The URL of targetted cloud service
        timout           (int)  Number of seconds until failed connection to cloud causes timeout
        return_variables (list) List of string variables that should want returning from cloud 
    """

    def __init__(self, URL:str, timeout:int=1, return_variables:list=[]):
        if not URL:
            raise TypeError("Provide a URL to Cloud Service")
        self.URL = URL
        self.return_variables = return_variables
        self.timeout = timeout

    def send_dataset(self, payload):
        """
        Sends user inputted JSON `payload` to object defined URL
        Returns a dictionary of variables expected from cloud and time client recieved
        """
        try:
            response = requests.post(self.URL, json=payload, timeout=self.timeout)
            client_recieve_time = datetime.now(timezone.utc)

            if response.status_code == 200:
                cloud_return = response.json()
                try:
                    if list:
                        feedback = {}
                        for variable in self.return_variables:
                            feedback[variable] = cloud_return.get(variable)
                            feedback['client_recieve_time'] = client_recieve_time
                        return feedback
                    else:
                        print("ERROR: No expected return from cloud")
                except TypeError("ERROR: variable(s) expect from cloud do not exist"):
                    return None
            else:
                print(f"ERROR: Cloud Status Code {response.status_code} ")
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Network Connection failed\n{e}")
            return None