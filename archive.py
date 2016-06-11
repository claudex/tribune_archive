#!/usr/bin/env python3

import argparse
import common
import logging
import pytz
import sqlalchemy
import time
import urllib.request

from bs4 import BeautifulSoup
from common import Config, Post, Tribune
from datetime import datetime
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser(description='Archive tribune post in ' +
        'database')

parser.add_argument('--initdb', help='Initialise the database (destroy all ' +
        'content)', action='store_true')

args = parser.parse_args()

if args.initdb:
    common.init()

engine = common.get_engine()
Session = sessionmaker(bind=engine)
session = Session()

conf = common.get_config()

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'TribuneArchive/0.1')]

while True: 
    for board_name in conf.get_boards():
        board_url = conf.get_parameter(board_name, 'backend')
        board_dateformat = conf.get_parameter(board_name, 'date')
        board_timezone = conf.get_parameter(board_name, 'timezone')
        board = session.query(Tribune).filter(Tribune.name == board_name).first()
        if not board:
            board = Tribune(name=board_name, timezone=board_timezone)
            session.add(board)

        boardxml = opener.open(board_url)
        soup = BeautifulSoup(boardxml, 'xml')

        board_tz = pytz.timezone(board.timezone)

        for post in soup.find_all('post'):
            parsed_date = datetime.strptime(post.get('time'),
                    board_dateformat).timestamp()
            date = datetime.fromtimestamp(parsed_date, board_tz)

            id = post.get('id')
            if not session.query(Post).filter( Post.post_id == id, Post.date ==
                    date, Post.tribune == board).count():
                info = post.find('info').text
                message = str(post.message)[9:-10]
                login = post.find('login').text

                plop = Post(post_id=id, date=date, info=info, message=message,
                        login=login, tribune=board)
                session.add(plop)
                session.commit()
                logging.debug('Adding %s: %s' % (board_name, plop))
    
    time.sleep(60)
