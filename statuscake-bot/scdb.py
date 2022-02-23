#!/usr/bin/env python
import os
import sys
import time
import MySQLdb
from helpers import Helpers
from config import Config
import requests

# Add pause
def add_pause(cur, test_info):
  query_info = []
  for key in test_info:
    query_info.append(test_info[key])

  query_values = tuple(query_info)
  sql = 'INSERT INTO paused_tests ' \
        '(test_id, domain_name, pause_start, pause_end, ' \
        'status, paused_by, unpaused_by) ' \
        'VALUES ' \
        '(%s, %s, %s, %s, %s, %s, %s)'
  try:
    cur.execute(sql, query_values)
    print('Added successfully!')
  except MySQLdb._exceptions.ProgrammingError as m:
    print(m)
  except MySQLdb._exceptions.OperationalError as m:
    print(m)

# Delete pause
def set_unpause(cur, test_info, cleanup_thread=None):
  sql_update = 'UPDATE paused_tests ' \
               'SET status = %s, unpaused_by = %s ' \
               'WHERE id = %s'

  if cleanup_thread:
    url = Config.API_URL + f'/{test_info[1]}'
    pause = {'paused': 'false'}
    Helpers.request_put(url, Config.AUTH_HEADERS, pause)
    query_values = ('unpaused', 'SCBot', test_info[0])
    print(query_values)
    cur.execute(sql_update, query_values)
  else:
    #  Get 'id' of most recent pause for the given domain
    select_values = (test_info['test_id'],)
    sql_select = 'SELECT id FROM paused_tests ' \
                 'WHERE test_id = %s'
    cur.execute(sql_select, select_values)
    last_pause = cur.fetchall()[-1]
    pause_id = last_pause[0]

    # Update most recent pause entry with the correct status, and unpause user
    query_values = ('unpaused', test_info['unpaused_by'], pause_id)
    print(query_values)
    cur.execute(sql_update, query_values)
    print('Updated entry successfully!')

# Constant cleaning check/remove
def clean_exp_pauses(cur):
  while True:
    now = int(time.time())
    cur.execute('SELECT id, test_id FROM paused_tests '
                'WHERE status = "paused" '
                'AND pause_end < %s', (now,))
    expired_pauses = cur.fetchall()
    print(expired_pauses)
    for pause in expired_pauses:
      set_unpause(cur, pause, True)

    time.sleep(5)


# Create and return a cursor
def get_cursor():
  db_conn = MySQLdb.connect(
      host = os.environ.get('DB_HOST'),
      port = int(os.environ.get('DB_PORT')),
      user = os.environ.get('DB_USER'),
      password = os.environ.get('DB_PASS'),
      database = os.environ.get('DB_NAME'),
      autocommit = True)

  cursor = db_conn.cursor()

  return cursor
