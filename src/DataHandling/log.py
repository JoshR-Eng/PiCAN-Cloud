import csv

class logger:

    def __init__(self, file_path:str, file_headers:list):
        self.file_path = file_path
        self.file_headers = file_headers
        self.writer = self.prepare_log_file()

    def prepare_log_file(self):
        with open(self.file_path, mode='w', newline='') as log:
            writer = csv.writer(log)
            writer.writerow(self.file_headers)

    def append(self):
        with open(self.file_path, mode='a', newline='') as log:
            writer = csv.writer(log)
            writer.writerow(self.file_headers)
