import os
import io
import mimetypes
from zipfile import ZipFile
import re
from datetime import datetime


class Message:
    def __init__(self, first_name, last_name, nickname, dt, text):
        self.first_name = first_name
        self.last_name = last_name
        self.nickname = nickname
        self.dt = datetime.strptime(dt, '%H:%M:%S %d/%m/%Y')
        self.text = text

    def as_dict(self):
        return {'first_name': self.first_name, 
                'last_name': self.last_name, 
                'nickname': self.nickname,
                'year': self.dt.year,
                'month': self.dt.month,
                'day': self.dt.day,
                'hour': self.dt.hour,
                'minute': self.dt.minute,
                'text': self.text}


class Reader:
    def __init__(self, path_to_data):
        

        self.path_to_data = path_to_data
        self.messages = []
        self.__parse_archive()
        

    def __check_file(self):
        # TODO: Сделать проверку на архив или текстовый файл
        # TODO: Сделать проверку на неправильный файл
        pass


    def __parse_archive(self):
        with ZipFile(self.path_to_data, 'r') as zipObj:
            for elem in zipObj.namelist():
                with io.TextIOWrapper(zipObj.open(elem), encoding="utf-8") as f:
                    self.__split_file_by_msg(f)

    def __split_file_by_msg(self, fd):
        text = []
        first = True
        for line in fd.readlines():
            if re.fullmatch(r'^\S.+\[\w+\]\s\(\d{2}:\d{2}:\d{2}\s+\d{2}/\d{2}/\d{4}\):\n$', line):
                if not first:
                    msg = Message(first_name, last_name, nickname, dt, '\n'.join(text))
                    self.messages.append(msg)
                    text = []
                else:
                    first = False
                splitted = line.split()
                if len(splitted) == 5:
                    first_name = splitted[0]
                    last_name = splitted[1]
                elif len(splitted) == 4:
                    first_name = splitted[0]
                    last_name = None
                nickname = splitted[-3][1:-1]
                dt = splitted[-2][1:] + ' ' + splitted[-1][:-2]

                continue
            
            text.append(line)






if __name__ == "__main__":
    rdr = Reader('data/C16-702 тру групп.zip')
    pass