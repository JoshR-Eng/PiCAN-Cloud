import csv
import os

class logger:

    def __init__(self, file_path:str, file_headers:list):
        if not file_path or not file_headers:
            raise ValueError("ERROR: Include file path and/or header")
        self.file_path = file_path
        self.file_headers = file_headers
        self.init_log_file()

    def init_log_file(self):
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, mode='w', newline='') as log:
                writer = csv.writer(log)
                writer.writerow(self.file_headers)
        except IOError as e:
            print(f"ERROR: Could not initialise log file at {self.file_path}: {e}")
            raise

    def append(self, data: dict[str: any]):
        try:
            # Create the row by looking up each header in the data dictionary
            # This ensures the data is always written in the correct column order
            with open(self.file_path, mode='a', newline='') as log_file:
                writer = csv.writer(log_file)
                writer.writerow(data)
        except (IOError, csv.Error) as e:
            print(f"ERROR: Failed to write to log file: {e}")
