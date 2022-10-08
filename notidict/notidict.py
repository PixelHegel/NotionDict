# -*- coding: utf-8 -*-

"""
NotiDict
NotiDict is a terminal dictionary application, you can use it to query the words from your own .mdx files,and the result will be shown by system notification. And it also supports uploading the result to Notion. You also can use it to upload highlight text to Notion. The best practice is to bind a shortcut to the app, then you can easily query the dict and highlight text anyevery.

Usage:
 notidict dict <word>
 notidict highlight <text>
 notidict -h | --help

Options:
 --help -h
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
import pyclip

#from notidict import __version__

def join(f):
    return os.path.join(os.path.dirname(__file__), f)


stream = open(join("config.yml"), 'r')
dictionary = yaml.safe_load(stream)
filename = dictionary['mdx_dict_path']
notion_vocabulary_database = dictionary['notion_vocabulary_database']
notion_highlight_database = dictionary['notion_highlight_database']
NOTION_API_KEY = os.getenv('NOTION_API_KEY')


def sendmessage(title, message):
    subprocess.Popen(['notify-send', title, message])
    return


def send_newword_to_notion(word, source, date, database):
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

    headers = {
        'Authorization': f"Bearer {NOTION_API_KEY}",
        'Notion-Version': '2022-06-28',
    }

    response = requests.post(
        'https://api.notion.com/v1/pages', headers=headers, json=json_data)
    return response


def create_new_page_with_conetent(title, content, date, database):
    url = "https://api.notion.com/v1/pages/"
    payload = json.dumps({
        "parent": {
            "database_id": database
        },
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "Updated": {
                "date": {
                    "start": date,
                    "end": None
                }
            }
        },
        "children": [
            {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ],
                "color":"default"
                }
            },
            {
            "type": "callout",
            "callout": {
                "rich_text": [{
                "type": "text",
                "text": {
                    "content": " "
                }
                }],
                "icon": {
                "emoji": "💡"
                },
                "color": "gray_background"
            }
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28',
        'Authorization': f"Bearer {NOTION_API_KEY}",

    }

    response = requests.request("POST", url, headers=headers, data=payload)
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
    return response.json()['results']


def update_highlight_to_page(title, content, database):
    url = "https://api.notion.com/v1/blocks/{0}/children".format(database)
    payload = json.dumps({
        "children": [
            {
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": content
                            }
                        }
                    ],
                "color":"default"
                }
            },
            {
            "type": "callout",
            "callout": {
                "rich_text": [{
                "type": "text",
                "text": {
                    "content": " "
                }
                }],
                "icon": {
                "emoji": "💡"
                },
                "color": "gray_background"
            }
            }
        ]
    })

    headers = {
        'Authorization':  f"Bearer {NOTION_API_KEY}",
        'Content-Type': 'application/json',
        'Notion-Version': '2022-06-28'
    }

    response = requests.request("PATCH", url, headers=headers, data=payload)


def get_selected_text(args):
    if args['dict']:
        var = args['<word>']
    else:
        var = args['<text>']
    return var


def get_application_title():
    gi.require_version("Wnck", "3.0")
    from gi.repository import Wnck
    scr = Wnck.Screen.get_default()
    scr.force_update()
    return scr.get_active_window().get_name()


def query_dict(args):
    source = get_application_title()
    content = get_selected_text(args)
    if len(content) > 3:
        headwords = [*MDX(filename)]
        items = [*MDX(filename).items()]
        queryword = content.lower().strip().replace(',', '').replace('.', '')

        word_index = headwords.index(queryword.encode())
        word, html = items[word_index]
        word, html = word.decode(), html.decode()

        soup = BeautifulSoup(html)

        sendmessage(word, str(soup))
        today = date.today().strftime("%Y-%m-%d")
        respone = send_newword_to_notion(
            word, source, today, notion_vocabulary_database)


def update_highlight(args):
    content = get_selected_text(args)
    if len(content) < 3:
        content = pyclip.paste()
        content = content.decode('utf-8')

    source = get_application_title()
    result = query_page_by_title(source, notion_highlight_database)

    if len(result) > 0:
        page_id = result[0]['id']
        update_highlight_to_page(source, content, page_id)
    else:
        today = date.today().strftime("%Y-%m-%d")
        respone = create_new_page_with_conetent(
            source, content, today, notion_highlight_database)
    sendmessage('Highlight saved to', source)


def init(args):
    if args["dict"]:
        query_dict(args)
    if args["highlight"]:
        update_highlight(args)


def main():
    args = docopt(__doc__)
    try:
        init(args)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
