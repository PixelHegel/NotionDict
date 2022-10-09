'''
Author: pixelhegel pixelhegel@gmail.com
Date: 2022-10-08 13:10:59
LastEditors: pixelhegel pixelhegel@gmail.com
LastEditTime: 2022-10-09 18:24:25
FilePath: /NotiDict/setup.py
Description: 

Copyright (c) 2022 by pixelhegel pixelhegel@gmail.com, All Rights Reserved. 
'''
#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from notidict import __version__


with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'readmdict',
    'requests',
    'docopt',
    'pyclip',
    'PyYAML'

]

setup(
    name='notidict',
    version=__version__,
    description='A high customized dictionary',
    long_description=readme,
    author='Pixelhegel',
    author_email='Pixelhegel@gmail.com',
    url='https://github.com/pixelhegel/notidict',
    packages=[
        'notidict',
    ],
    package_dir={'notidict':
                 'notidict'},
    include_package_data=True,
    package_data={'': ['config.yml','get_active_window_title_macos.scpt']},
    install_requires=requirements,
    license='Apache License',
    zip_safe=False,
    keywords='dictionary notification tool',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'notidict=notidict.notidict:main',
        ],
    },
)