import csv
import os
from datetime import datetime

class logger:

    def __init__(self, directory_path:str, file_headers:list):
        if not directory_path or not file_headers:
            raise ValueError("ERROR: Include file path and/or header")
        self.directory_path = directory_path
        self.file_headers = file_headers
        self.file_path=self.init_log_file()

    def init_log_file(self) -> str:
        try:
            os.makedirs(self.directory_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            file_name = f"log_{timestamp}.csv"
            file_path = os.path.join(self.directory_path, file_name)

            with open(file_path, mode='w', newline='') as log:
                writer = csv.writer(log)
                writer.writerow(self.file_headers)
            return file_path
        except IOError as e:
            print(f"ERROR: Could not initialise log file at {self.directory_path}: {e}")
            raise

    def append(self, data: dict):
        try:
            # Create the row by looking up each header in the data dictionary
            # This ensures the data is always written in the correct column order
            row_data = [data.get(header) for header in self.file_headers]
            with open(self.file_path, mode='a', newline='') as log_file:
                writer = csv.writer(log_file)
                writer.writerow(row_data)
        except (IOError, csv.Error) as e:
            print(f"ERROR: Failed to write to log file: {e}")
