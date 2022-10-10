=============================================================================
``NotionDict`` - A terminal dictionary application
=============================================================================
.. image:: https://api.travis-ci.com/PixelHegel/NotionDict.svg?branch=main
        :target: https://app.travis-ci.com/github/PixelHegel/NotionDict


NotionDict
----------
NotionDict是一个命令行字典工具，可以查询在任何应用鼠标选中的词，查询结果以系统通知方式呈现，并将该词上传到Notion中。统全局快捷键，进而方便的使用。

NotionDict
----------
NotionDict is a terminal dictionary application, you can use it to query the words from your own .mdx files,and the result will be shown by system notification. And it also supports uploading the result to Notion. You also can use it to upload highlight text to Notion. The best practice is to bind a shortcut to the app, then you can easily query the dict and highlight text anyevery.

Installation | 安装
------------

::

    pip install notiondict

Usage | 使用
-----

::

    Usage:
    notiondict dict <word> [--config <file-path>]
    notiondict highlight <text> [--config <file-path>]
    notiondict -h | --help

    Options:
    --config <file-path>  your own config file
    --help -h  show help

Examples | 示例
---------

::

    notiondict dict book --config /home/username/config.yml
    notiondict highlight "This is a highlight"


Contents of requirements.txt

::

    docopt==0.6.2
    pyclip==0.6.0
    PyYAML==6.0
    readmdict==0.1.1
    requests==2.28.1
    setuptools==63.0.0
    urllib3==1.26.12