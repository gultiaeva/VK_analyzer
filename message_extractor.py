import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import emoji
import numpy as np
import collections


class MessageExtractor():
    def __init__(self, messages_file):
        self.stopwords = self._load_stopwords()
        self.path_to_messages = messages_file

    def _load_stopwords(self):
        '''
        Function that loads stopwords
        '''

        with open('./data/stopwords', 'r') as f:
            text = f.read()
        return text.split()

    def _load_messages(self):
        msgs = []
        with open(self.path_to_messages, 'r', encoding='utf8') as f:
            tmp = f.readline()
            for line in f:
                if re.search(r'^[^\s].+\(\d{2}:\d{2}:\d{2}  \d{2}/\d{2}/\d{4}\):', line):
                    msgs.append(tmp)
                    tmp = line
                else:
                    tmp += line
            return msgs
    
    def _clean(self, messages):
        fullmsgs = [' '.join(msg for msg in message.split('\n')[1:]) 
            for message in messages]
        datesnames = [''.join(msg for msg in message.split('\n')[0]) 
            for message in messages]
        dates = [re.search(r'\(\d{2}:\d{2}:\d{2}  \d{2}/\d{2}/\d{4}\):', 
            datename).group(0)[1:-2] for datename in datesnames]
        names = [re.search(r'(.*)\(\d{2}:\d{2}:\d{2}  \d{2}/\d{2}/\d{4}\):', 
            datename).group(1)[:-1] for datename in datesnames]

        for i in range(len(fullmsgs)):
            if re.search(r'\t.+\(\d{2}:\d{2}:\d{2}  \d{2}/\d{2}/\d{4}\):', fullmsgs[i]):
                fullmsgs[i] = 'Пересланное сообщение'
            elif 'Attachment' in fullmsgs[i]:
                fullmsgs[i] = 'Attachment'
            else:
                fullmsgs[i] = fullmsgs[i].strip()
                
        raw_data = pd.DataFrame({'date': dates, 
              'name': names, 
              'message': fullmsgs})

        return raw_data

    def extract_messages(self):
        self.messages_df = self._clean(self._load_messages)
        return self.messages_df


