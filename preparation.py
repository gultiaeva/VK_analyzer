import os
import pandas as pd
import re
import nltk
from functools import lru_cache
from multiprocessing import Pool
import emoji


class FileNotValidException(IOError):
    pass


class Extractor():

    def __init__(self, messages_file):
        self.path_to_messages = messages_file

    def _check_if_valid(self):
        pass

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
        fullmsgs = [' '.join(msg for msg in message.split('\n')[1:]) for message in messages]
        datesnames = [''.join(msg for msg in message.split('\n')[0]) for message in messages]
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
        self.messages_df = self._clean(self._load_messages())
        return self.messages_df


class Preparer():
    
    def __init__(self, data):
        self.df = data
        self.stopwords = self._load_stopwords()        
        # print('Stopwords loaded!')


    def _load_stopwords(self):
        '''
        Function that loads stopwords
        '''

        with open('./data/stopwords', 'r') as f:
            text = f.read()
        return text.split()


    def _add_columns(self):
        '''
        Function adds columns to the DataFrame for future use
        '''
        self.df['date'] = pd.to_datetime(self.df['date'], format=r'%H:%M:%S %d/%m/%Y')

        self.df['year'] = self.df['date'].apply(lambda ts: ts.year)
        self.df['month'] = self.df['date'].apply(lambda ts: ts.month)
        self.df['day'] = self.df['date'].apply(lambda ts: ts.day)
        self.df['hour'] = self.df['date'].apply(lambda ts: ts.hour)
        self.df['minute'] = self.df['date'].apply(lambda ts: ts.minute)
        self.df['second'] = self.df['date'].apply(lambda ts: ts.second)
        self.df['message_len'] = self.df['message'].apply(len)
        self.df['emojis'] = self.df['message'].apply(emoji.emoji_count)

        cpus = os.cpu_count()
        with Pool(processes=cpus) as pool:
            self.df['message'] = pool.map(self._normalize_text, self.df['message'])

    @lru_cache(maxsize=1000000)
    def _normalize_text(self, text):
        text = text.lower()
        if 'пересланное' in text or 'attachment' in text or 'http' in text:
            return text
        return ' '.join([word for word in re.findall(r'\w+', text)
                        if word not in self.stopwords])

    def prepare(self):
        self._add_columns()
        return self.df


if __name__ == '__main__':
    extractor = Extractor('examples/messages.txt')
    messages = extractor.extract_messages()
    print(messages)
