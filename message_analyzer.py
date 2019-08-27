from extraction import MessageExtractor
from preparation import Preparer
from draw import Drawer
import sys

if __name__ == '__main__':
    df = MessageExtractor('./examples/messages.txt').extract_messages()
    prep = Preparer(df).prepare()
    drawer = Drawer(prep)
    drawer.draw_all()
