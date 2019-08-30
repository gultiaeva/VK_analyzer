from preparation import Extractor, Preparer, FileNotValidException
from draw import Drawer
import sys


class MessageAnalyzer():
    def __init__(self, filename):
        self.filename = filename
        self.extracted = Extractor(filename).extract_messages()

    def analyze(self):
        prepared_messages = Preparer(self.extracted).prepare()
        drawer = Drawer(prepared_messages)
        drawer.draw_all()


if __name__ == '__main__':
    analyzer = MessageAnalyzer('./examples/messages.txt')
    analyzer.analyze()
