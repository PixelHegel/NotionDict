"""
NotiDict.
Describe what this script does

Usage:
 notidict --dict
 notidict --highlight
 name -h | --help

Options:
  --dict query the selected word
  --highlight send the selected sentence to notion
"""
import os
import json
import subprocess
from datetime import date
import sys

import gi
import requests
from bs4 import BeautifulSoup
from pyquery import PyQuery as pq
from readmdict import MDD, MDX
import yaml
from docopt import docopt

from notidict import __version__

stream = open("notidict/config.yml", 'r')
dictionary = yaml.safe_load(stream)
filename = dictionary['mdx_dict_path']
notion_vocabulary_database = dictionary['notion_vocabulary_database']


def sendmessage(title, message):
    subprocess.Popen(['notify-send', title, message])
    return


def send_newword_to_notion(word, source, date, database):
    NOTION_API_KEY = os.getenv('NOTION_API_KEY')

    headers = {
        'Authorization': f"Bearer {NOTION_API_KEY}",
        # 'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28',
    }

    json_data = {
        "parent": {
            "database_id": database
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": word
                        }
                    }
                ]
            },
            "Source": {

                "type": "rich_text",
                "rich_text": [
                    {
                        "type": "text",
                        "text": {"content": source}
                    }
                ]


            },

            "Date": {
                "date": {
                    "start": date,
                    "end": None
                }
            }
        }
    }

    response = requests.post(
        'https://api.notion.com/v1/pages', headers=headers, json=json_data)
    return response


def query_page_by_title(title, database):
    url = "https://api.notion.com/v1/databases/{0}/query".format(database)

    payload = json.dumps({
        "filter": {
            "property": "Name",
            "rich_text": {
                "contains": title
            }
        }
    })
    headers = {
        'Authorization':  f"Bearer {NOTION_API_KEY}",
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()['result']


def get_selected_text():
    var = os.popen('xsel').read()
    return var


def query_dict():
    gi.require_version("Wnck", "3.0")
    from gi.repository import Wnck
    scr = Wnck.Screen.get_default()
    scr.force_update()
    source = scr.get_active_window().get_name()

    var = get_selected_text()
    headwords = [*MDX(filename)]

    items = [*MDX(filename).items()]

    queryword = var.lower().strip().replace(',', '').replace('.', '')

    word_index = headwords.index(queryword.encode())
    word, html = items[word_index]
    word, html = word.decode(), html.decode()

    soup = BeautifulSoup(html)

    sendmessage(word, str(soup))
    today = date.today().strftime("%Y-%m-%d")
    respone = send_newword_to_notion(
        word, source, today, notion_vocabulary_database)


def init(args):
    if args["--dict"]:
        query_dict()
    if args["--highlight"]:
        print("TODO")


def main():
    args = docopt(__doc__, version=__version__)
    try:
        init(args)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
