import json
from collections import deque

class CAN_buffer:

    """
    A buffer class to store and work with data coming 
    in from CAN bus before going to the cloud
    Built on Pythons's efficient deque to ensure memory limitation and data relavance
    """

    def __init__(self, buffer_size: int=200):
        """
        Initialises the buffer
        `buffer size (int) : max number of items the buffer will hold.
                             When buffer full, new data will push out the oldest
        """
        if not isinstance(buffer_size, int) or buffer_size<=0:
            raise ValueError("ERROR: Buffer size must be positive integer")
        self.buffer = deque(maxlen=buffer_size)
        

    def append(self, item: any):
        self.buffer.append(item)

    def flush(self):
        self.buffer.clear()

    def return_as_json(self):
        return json.dumps(list(self.buffer), indent=4)