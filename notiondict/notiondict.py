# -*- coding: utf-8 -*-

"""
NotionDict
NotionDict is a terminal dictionary application, you can use it to query the words from your own .mdx files,and the result will be shown by system notification. And it also supports uploading the result to Notion. You also can use it to upload highlight text to Notion. The best practice is to bind a shortcut to the app, then you can easily query the dict and highlight text anyevery.

Usage:
 notiondict dict <word> [--config <file-path>]
 notiondict highlight <text> [--config <file-path>]
 notiondict -h | --help

Options:
 --config <file-path>   show config
 --help  -h show help info
 --version  

Examples:
 notiondict dict book --config /home/username/config.yml
 notiondict highlight "This is a highlight"
"""
import json
import os
import subprocess
import sys
from datetime import date

import pyclip
import requests
import yaml
from docopt import docopt
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

sysstr = sys.platform

from notiondict import __version__
DICT_PATH = ""
NOTION_VOCABULARY_DATABASE = ""
NOTION_HIGHLIGHT_DATABASE = ""
NOTION_API_KEY = ""


def join(f):
    return os.path.join(os.path.dirname(__file__), f)

def displayNotification(message,title=None,subtitle=None,soundname=None):
    """
        Display an OSX notification with message title an subtitle
        sounds are located in /System/Library/Sounds or ~/Library/Sounds
    """
    titlePart = ''
    if(not title is None):
        titlePart = 'with title "{0}"'.format(title)
    subtitlePart = ''
    if(not subtitle is None):
        subtitlePart = 'subtitle "{0}"'.format(subtitle)
    soundnamePart = ''
    if(not soundname is None):
        soundnamePart = 'sound name "{0}"'.format(soundname)

    appleScriptNotification = 'display notification "{0}" {1} {2} {3}'.format(message,titlePart,subtitlePart,soundnamePart)
    os.system("osascript -e '{0}'".format(appleScriptNotification))

def sendmessage(title, message):
    if sysstr == 'linux':
        subprocess.Popen(['notify-send', title, message])
    elif sysstr == 'darwin':
        displayNotification(message=message,title=title)
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

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=3)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    try:
        response = session.post(
            'https://api.notion.com/v1/pages', headers=headers, json=json_data)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
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
            "Date": {
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

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=3)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    try:
        response = session.post(url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
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

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=3)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    try:
        response = session.post(url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
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

    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=3)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    try:
        response = session.patch(url, headers=headers, data=payload)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

    return response


def get_selected_text(args):
    if args['dict']:
        var = args['<word>']
    else:
        var = args['<text>']
    return var


def get_application_title():
    if sysstr == 'linux':
        import gi
        gi.require_version("Wnck", "3.0")
        from gi.repository import Wnck
        scr = Wnck.Screen.get_default()
        scr.force_update()
        return scr.get_active_window().get_name()
    elif sysstr == 'darwin':
        scpt_path = join("get_active_window_title_macos.scpt")
        try:
            title = subprocess.check_output(['osascript', scpt_path])
        except:
            logging.error("Can't find active window")
        finally:
            return title.decode('utf-8')


def query_dict(args,MDX,MDD):
    source = get_application_title()
    content = get_selected_text(args)
    if len(content) > 3:
        headwords = [*MDX(DICT_PATH)]
        items = [*MDX(DICT_PATH).items()]
        queryword = content.lower().strip().replace(',', '').replace('.', '')

        word_index = headwords.index(queryword.encode())
        word, html = items[word_index]
        word, html = word.decode(), html.decode()
        message = str(html)[0:90]
        sendmessage(word, message)
        today = date.today().strftime("%Y-%m-%d")
        response = send_newword_to_notion(
            word, source, today, NOTION_VOCABULARY_DATABASE)


def update_highlight(args):
    content = get_selected_text(args)
    if len(content) < 3:
        content = pyclip.paste()
        content = content.decode('utf-8')

    source = get_application_title()
    result = query_page_by_title(source, NOTION_HIGHLIGHT_DATABASE)

    if len(result) > 0:
        page_id = result[0]['id']
        update_highlight_to_page(source, content, page_id)
    else:
        today = date.today().strftime("%Y-%m-%d")
        response = create_new_page_with_conetent(
            source, content, today, NOTION_HIGHLIGHT_DATABASE)
    sendmessage('Highlight saved to', source)


def init(args):
    print(args)
    if args['--config']:
        stream = open(args['--config'], 'r')
    else:
        stream = open(join("config.yml"), 'r')
    dictionary = yaml.safe_load(stream)
    global DICT_PATH
    global NOTION_HIGHLIGHT_DATABASE
    global NOTION_VOCABULARY_DATABASE
    global NOTION_API_KEY

    try:

        NOTION_API_KEY = os.getenv('NOTION_API_KEY')
        DICT_PATH = os.getenv('DICT_PATH')
        NOTION_VOCABULARY_DATABASE = os.getenv('NOTION_VOCABULARY_DATABASE')
        NOTION_HIGHLIGHT_DATABASE = os.getenv('NOTION_HIGHLIGHT_DATABASE')

        if DICT_PATH is None:
            DICT_PATH = dictionary['DICT_PATH']

        if NOTION_VOCABULARY_DATABASE is None:
            NOTION_VOCABULARY_DATABASE = dictionary['NOTION_VOCABULARY_DATABASE']

        if NOTION_HIGHLIGHT_DATABASE is None:
            NOTION_HIGHLIGHT_DATABASE = dictionary['NOTION_HIGHLIGHT_DATABASE']

        if NOTION_API_KEY is None:
            NOTION_API_KEY = dictionary['NOTION_API_KEY']

    except Exception as exc:
        logging.error("Please put your Notion info into the env variables or config file")

    if args["dict"]:
        from readmdict import MDD, MDX
        query_dict(args,MDX,MDD)
    if args["highlight"]:
        update_highlight(args)


def main():
    args = docopt(__doc__, version=__version__)
    try:
        init(args)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
