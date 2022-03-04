#!/usr/bin/env python
'''Database operations for StatusCake bot'''
import os
import time
import MySQLdb
from helpers import Helpers
from config import Config
from logs import ScbotLogger

db_logger = ScbotLogger('scdb')

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
    db_logger.info(f'PAUSE added to db for {test_info["domain_name"]}',
                   test_info['paused_by'])
  except MySQLdb.ProgrammingError as m:
    err = m.args
    db_logger.critical(str(err[0]) + ' ' + err[1], 'add_pause')
    db_logger.error(query_values, 'add_pause')
    db_logger.error(test_info, 'add_pause')
  except MySQLdb.OperationalError as m:
    err = m.args
    db_logger.critical(str(err[0]) + ' ' + err[1], 'add_pause')
    db_logger.error(query_values, 'add_pause')
    db_logger.error(test_info, 'add_pause')

# Delete pause
def set_unpause(cur, test_info, cleanup_thread=None):
  sql_update = 'UPDATE paused_tests ' \
               'SET status = %s, unpaused_by = %s ' \
               'WHERE id = %s'

  if cleanup_thread:
    url = Config.API_URL + f'/{test_info[1]}'
    pause = {'paused': 'false'}
    Helpers.request_put(url, Config.AUTH_HEADERS, pause)
    db_logger.info(f'RESUME {test_info[-1]}', 'SCBot Cleanup')
    query_values = ('unpaused', 'SCBot', test_info[0])
    try:
      cur.execute(sql_update, query_values)
      db_logger.info(f'Removed pause from database: {test_info[-1]}',
                     'SCBot Cleanup')
    except MySQLdb.ProgrammingError as m:
      err = m.args
      db_logger.critical(str(err[0]) + ' ' + err[1], 'set_unpause_cleanup')
      db_logger.error(query_values, 'set_unpause_cleanup')
      db_logger.error(test_info, 'set_unpause_cleanup')

  else:
    #  Get 'id' of most recent pause for the given domain
    select_values = (test_info['test_id'],)
    sql_select = 'SELECT id FROM paused_tests ' \
                 'WHERE test_id = %s'
    try:
      cur.execute(sql_select, select_values)
    except MySQLdb.ProgrammingError as m:
      err = m.args
      db_logger.critical(str(err[0]) + ' ' + err[1], 'set_unpause')
      db_logger.error(query_values, 'set_unpause')
      db_logger.error(test_info, 'set_unpause')

    last_pause = cur.fetchall()[-1]
    pause_id = last_pause[0]

    # Update most recent pause entry with the correct status, and unpause user
    query_values = ('unpaused', test_info['unpaused_by'], pause_id)
    try:
      cur.execute(sql_update, query_values)
      db_logger.info(f'Set pause {pause_id} to UNPAUSED: '
                     f'{test_info["domain_name"]}',
                     test_info['unpaused_by'])
    except MySQLdb.ProgrammingError as m:
      err = m.args
      db_logger.critical(str(err[0]) + ' ' + err[1], 'set_unpause')
      db_logger.error(query_values, 'set_unpause')
      db_logger.error(test_info, 'set_unpause')
    print('Updated entry successfully!')

# Constant cleaning check/remove
def clean_exp_pauses(cur):
  while True:
    now = int(time.time())
    cur.execute('SELECT id, test_id, domain_name FROM paused_tests '
                'WHERE status = "paused" '
                'AND pause_end < %s', (now,))
    expired_pauses = cur.fetchall()
    for pause in expired_pauses:
      set_unpause(cur, pause, True)

    time.sleep(5)


# Create and return a cursor
def get_connection():
  try:
    db_conn = MySQLdb.connect(
        host = os.environ.get('DB_HOST'),
        port = int(os.environ.get('DB_PORT')),
        user = os.environ.get('DB_USER'),
        password = os.environ.get('DB_PASS'),
        database = os.environ.get('DB_NAME'),
        autocommit = True)
    return db_conn
  except MySQLdb.OperationalError as e:
    err = e.args
    db_logger.critical(str(err[0]) + ' ' + err[1], 'get_conn')
    db_logger.info(os.environ, 'get_conn')

def get_cursor():
  db_conn = get_connection()
  cursor = db_conn.cursor()

  return cursor
