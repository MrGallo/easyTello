from datetime import datetime
from typing import List, Union


class Stats:
    stats: List["Stats"] = []

    def __init__(self, command: str):
        self.command = command
        self.response = None
        self.id = len(Stats.stats)

        self.start_time = datetime.now()
        self.end_time = None
        self.duration = None

        Stats.stats.append(self)

    def add_response(self, response: str):
        self.response = str(response)
        # Calculating total time taken to execute command
        self.end_time = datetime.now()
        self.duration = (self.end_time-self.start_time).total_seconds()

    def got_response(self):
        return self.response is not None

    def get_raw_response(self):
        return self.response

    def numeric_response(self, data: str):
        num_val = ''.join(i for i in data if i.isdigit() or i=='-' or i=='.')
        return num_val

    def int_response(self, data: str):
        return int(self.numeric_response(data))

    def float_response(self, data: str):
        return float(self.numeric_response(data))
    
    def attitude_response(self):
        raw_att = self.response.split(';')
        att_data = (self.int_response(raw_att[0]), self.int_response(raw_att[1]), self.int_response(raw_att[2]))
        return att_data
    
    def acceleration_response(self):
        raw_acc = self.response.split(';')
        acc_data = (self.float_response(raw_acc[0]), self.float_response(raw_acc[1]), self.float_response(raw_acc[2]))
        return acc_data

    def temp_response(self):
        raw_temp = self.response.split('~')
        temp = (self.int_response(raw_temp[0]) + self.int_response(raw_temp[1]))/2
        return temp

    def sdk_response(self):
        sdk = self.response
        return sdk

    def get_response(self) -> Union[str, int]:
        if 'attitude?' in self.command:
            return self.attitude_response()
        elif 'acceleration?' in self.command:
            return self.acceleration_response()
        elif 'temp?' in self.command:
            return self.temp_response()
        elif 'baro?' in self.command or 'speed?' in self.command:
            return self.float_response(self.response)
        elif 'sdk?' in self.command:
            return self.sdk_response()
        elif '?' not in self.command:
            return self.get_raw_response()
        else:
            return self.int_response(self.response)
