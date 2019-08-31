from os import makedirs, path
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import wordcloud
from tqdm import tqdm

class NotDrawnYetException(Exception):
    pass

class Drawer():
    def __init__(self, data, persons=None):
        self.df = data
        self.names = self.select_persons() if persons is None else persons
        self.is_drawn = False

    def select_persons(self):
        return self.df['name'].unique()

    def draw_symbols_per_person(self):
        chars_per_person = self.df.groupby('name')['message_len'].sum()
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 9))
        ax.pie(chars_per_person.values, labels=chars_per_person.index)
        ax.set_title('Распределение количества отправленных символов')
        return fig

    def draw_messages_per_person(self):
        msg_per_person = self.df.groupby('name')['message'].count()
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 9))
        ax.pie(msg_per_person.values, labels=msg_per_person.index)
        ax.set_title('Распределение количества отправленных сообщений')
        return fig
        
    
    def draw_emotes_per_person(self):
        emojis_per_person = self.df.groupby('name')['emojis'].sum()
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 9))
        ax.pie(emojis_per_person.values, labels=emojis_per_person.index)
        ax.set_title('Распределение количества отправленных emoji')
        return fig
        
    def draw_most_common_words(self):
        wordcount = {}
        for name in self.names:
            tmp = []
            for msg in self.df[self.df['name'] == name]['message']:
                if 'пересланное' in msg or 'attachment' in msg or 'http' in msg:
                    continue
                for word in msg.split():
                    if len(word) >= 4:
                        tmp.append(word)
            wordcount[name] = Counter(tmp)

        plots = []
        for name in self.names:
            mc = np.array(wordcount[name].most_common(30))
            fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 9))
            sns.barplot(ax=ax, x=mc[:, 0], y=mc[:, 1].astype('int64'))
            ax.set_xlabel('Слова')
            ax.set_ylabel('Частота')
            ax.set_title('Частота употребления слов для ' + name)
            ax.xaxis.set_tick_params(rotation=90)
            plots.append((fig, 'common_words' + name + '.png'))
        return plots
            
    def draw_wordclouds_each_person(self):
        clouds = []
        for name in self.names:
            tmp = ' '.join(msg for msg in self.df[self.df['name'] == name]['message'] 
                           if 'пересланное' not in msg 
                           and 'attachment' not in msg 
                           and 'http' not in msg)

            cloud = wordcloud.WordCloud(width=1920, 
                                        height=1080, 
                                        background_color='white').generate(tmp)
            
            clouds.append((cloud, 'wordclouds/cloud ' + name + '.png'))
        return clouds
    
    def draw_wordcloud_all(self):
        tmp = ' '.join(msg for msg in self.df['message'] 
                       if 'пересланное' not in msg 
                       and 'attachment' not in msg 
                       and 'http' not in msg)

        cloud = wordcloud.WordCloud(width=1920, 
                                    height=1080, 
                                    background_color='white').generate(tmp)
        return cloud

    def draw_messages_per_hour_distribution(self):
        dist_hours = self.df.groupby('hour')['message'].count()
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 9))
        sns.barplot(ax=ax, x=dist_hours.index, y=dist_hours.values, palette='PuBuGn_d')
        ax.set_xlabel('Часы')
        ax.set_ylabel('Количество сообщений')
        ax.set_title('Распределение сообщений по часам в сутках')
        return fig
        
    def draw_messages_count_heatmap(self):
        crosstab = pd.pivot_table(self.df, 
                                  index=['year', 'month'], 
                                  values='message',
                                  columns='day',
                                  aggfunc='count',
                                  fill_value=0)
        
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(16, 9))
        ax = sns.heatmap(data=crosstab, annot=True, fmt='d', 
                         cmap='Reds', ax=ax, square=True, cbar=False)
        ax.set_xlabel('День')
        ax.set_ylabel('Год/месяц')
        ax.set_title('Тепловая карта сообщений')
        ax.set_aspect('equal')
        return fig

    def _save_figure(self, figure, path):
        figure.savefig(path, dpi=300,
                       bbox_inches='tight', 
                       pad_inches=0.5)

    def draw_all(self):
        print('Drawing your plots:')
        with tqdm(total=100) as pbar:
            self.messages_per_person = self.draw_messages_per_person()
            pbar.update(12.5)
            self.symbols_per_person = self.draw_symbols_per_person()
            pbar.update(12.5)
            self.emotes_per_person = self.draw_emotes_per_person()
            pbar.update(12.5)
            self.most_common_words = self.draw_most_common_words()
            pbar.update(12.5)
            self.messages_per_hour_dist = self.draw_messages_per_hour_distribution()
            pbar.update(12.5)
            self.wordclouds_each_person = self.draw_wordclouds_each_person()
            pbar.update(12.5)
            self.wordcloud_all = self.draw_wordcloud_all()
            pbar.update(12.5)
            self.messages_count_heatmap = self.draw_messages_count_heatmap()
            pbar.update(12.5)

        self.is_drawn = True

    def save_all(self, directory):
        if not self.is_drawn:
            raise NotDrawnYetException('Not yet!')

        if not path.exists(directory):
            makedirs(directory)
        print('Saving tour plots:')
        with tqdm(total=100) as pbar:
            self._save_figure(self.symbols_per_person,
                            path.join(directory, 'symbols_per_person.png'))
            pbar.update(12.5)
            self._save_figure(self.messages_per_person,
                            path.join(directory, 'messages_per_person.png'))
            pbar.update(12.5)
            self._save_figure(self.emotes_per_person,
                            path.join(directory, 'emotes_per_person.png'))
            pbar.update(12.5)
            self._save_figure(self.messages_per_hour_dist,
                            path.join(directory, 'messages_per_hour.png'))
            pbar.update(12.5)
            self._save_figure(self.messages_count_heatmap,
                            path.join(directory, 'message_heatmap.png'))
            pbar.update(12.5)
            for fig, fname in self.most_common_words:
                self._save_figure(fig, path.join(directory, fname))
            pbar.update(12.5)
            
            makedirs(path.join(directory, 'wordclouds'), exist_ok=True)

            for fig, fname in self.wordclouds_each_person:
                fig.to_file(path.join(directory, fname))
            pbar.update(12.5)

            self.wordcloud_all.to_file(path.join(directory, 'wordclouds/cloud_all_users.png'))
            pbar.update(12.5)