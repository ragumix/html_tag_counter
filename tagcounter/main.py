import sys
import requests
import click
import sqlite3
import pickle
import os
import yaml
import tkinter as tk
from loguru import logger
from html.parser import HTMLParser


class MyHTMLParser(HTMLParser):
    def __init__(self, dic):
        HTMLParser.__init__(self)
        self.d = dic

    def handle_starttag(self, tag, attrs):
        if tag in self.d:
            self.d[tag] += 1
        else:
            self.d[tag] = 1

    def handle_endtag(self, tag):
        self.d[tag] += 1


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.bottomframe = tk.Frame(self)
        self.bottomframe.pack(side="bottom")

        self.label = tk.Label(self, width=15, text="Type a webpage:")
        self.label.pack(side="left")

        self.entry = tk.Entry(self)
        self.entry.pack(side="left")

        self.calc = tk.Button(self)
        self.calc["text"] = "Calculate"
        self.calc["command"] = self.in_count
        self.calc.pack(side="left")

        self.view = tk.Button(self)
        self.view["text"] = "View from database"
        self.view["command"] = self.view_from_db
        self.view.pack(side="left")

        self.text = tk.Text(self.bottomframe)
        self.text.pack(side="bottom")

        self.text2 = tk.Text(self.bottomframe, width=35, height=1)
        self.text2.pack(side="bottom")

    def in_count(self):
        self.text.delete(1.0, "end")
        self.text2.delete(1.0, "end")
        url = check_in_dict(self.entry.get())
        try:
            tags, date = count(url)
        except:
            self.text2.insert(1.0, "Error! Please type a correct webpage.")
        else:
            insert_to_db(tags, url, date)
            self.text.insert(1.0, tags)
            self.text2.insert(1.0, "Finished.")

    def view_from_db(self):
        self.text.delete(1.0, "end")
        self.text2.delete(1.0, "end")
        url = check_in_dict(self.entry.get())
        try:
            tags = get_from_db(url)
        except:
            self.text2.insert(1.0, "This webpage doesn't exist in DB.")
        else:
            self.text.insert(1.0, tags)
            self.text2.insert(1.0, "Finished.")


def count(url):
    response = requests.get("http://" + url)
    dict = {}
    parser = MyHTMLParser(dict)
    parser.feed(response.content.decode(response.encoding))
    date = response.headers['Date']
    logger.info(response.url)
    return dict, date


def insert_to_db(tags, url, date):
    pdata = pickle.dumps(tags, pickle.HIGHEST_PROTOCOL)
    domain = url.split('.')[-2]

    path = os.path.join(os.getcwd(), 'requests.db')
    conn = sqlite3.connect(path)
    c = conn.cursor()
    #Check if the database 'requests' exists
    c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='requests'")
    if c.fetchone()[0] != 1:
        c.execute("CREATE table requests (name text, url text, date text, tags blob);")
    c.execute("INSERT INTO requests (name, url, date, tags) VALUES (?, ?, ?, ?)",
              (domain, url, date, sqlite3.Binary(pdata)))
    conn.commit()
    conn.close()
    return True


def get_from_db(url):
    conn = sqlite3.connect('requests.db')
    c = conn.cursor()
    #Check if the database 'requests' exists
    c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='requests'")
    if c.fetchone()[0] != 1:
        c.execute("CREATE table requests (name text, url text, date text, tags blob);")
    c.execute("SELECT tags FROM requests WHERE (url = ?)", (url,))
    data = c.fetchone()[0]
    conn.commit()
    conn.close()
    return pickle.loads(data)


def check_in_dict(url):
    filename = os.path.join(os.getcwd(), 'synonims.yaml')
    f = open(filename, 'w+')
    if not os.path.exists(filename) or len(f.read()) == 0:
        f.write('ggl: google.com')
        f.close()
    with open(filename, "r") as f:
        dict = yaml.load(f, Loader=yaml.FullLoader)
    if url in dict.keys():
        return dict[url]
    else:
        return url


@click.command()
@click.option('--get', help='Get number of HTML tags on the webpage.')
@click.option('--view', help='Read saved data from database for the corresponding webpage.')
def main(*args, **kwargs):
    path = filename = os.path.join(os.getcwd(), 'requests.log')
    logger.add(path, format="{time:YYYY-MM-DD HH:mm:ss.SSS} {message}", rotation="1 week")
    if kwargs['get'] is not None:
        url = check_in_dict(kwargs['get'])
        try:
            tags, date = count(url)
        except:
            print("Error! Please type correct webpage.")
            sys.exit(1)
        insert_to_db(tags, url, date)
        print(tags)
        pass
    elif kwargs['view'] is not None:
        url = check_in_dict(kwargs['view'])
        try:
            print(get_from_db(url))
        except:
            print("This webpage doesn't exist in DB.")
        pass
    else:
        root = tk.Tk()
        app = Application(master=root)
        app.mainloop()


if __name__ == "__main__":
    main()
