import os
import pandas as pd
import re
import nltk
from functools import lru_cache
from multiprocessing import Pool
import emoji


class Preparer():
    
    def __init__(self, data):
        self.df = data
        self.stopwords = self._load_stopwords()        
        print('Stopwords loaded!')


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