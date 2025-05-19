from html.parser import HTMLParser


class HTMLCleaner(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ""

    def handle_data(self, data):
        self.text += data

    def clean(self, html):
        self.text = ""
        self.feed(html)
        return self.text.strip()
