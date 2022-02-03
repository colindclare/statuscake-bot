#!/usr/bin/env python
import os
import sys
import mariadb

# Try setting paramstyle on import
mariadb.paramstyle = 'pyformat'

# Add pause
def add_pause(cur, test_info):
  sql = "INSERT INTO paused_tests "\
        "(test_id, domain_name, pause_start, pause_end, user_name)"\
        "VALUES "\
        "(?, ?, ?, ?, ?)"
        #"(%{test_id}, %{domain_name}, %{pause_start}, %{pause_end}, %{user})"

  cur.execute(sql, test_info)

# Delete pause
def delete_pause(cur, pause_id):
  print('Delete pause from DB')

# Constant cleaning check/remove
def clean_pauses(cur):
  print('Running cleanup loop')

# Create and return a cursor
def get_cursor():
  db_conn = mariadb.connect(
      host = os.environ.get('DB_HOST'),
      port = int(os.environ.get('DB_PORT')),
      user = os.environ.get('DB_USER'),
      password = os.environ.get('DB_PASS'),
      database = os.environ.get('DB_NAME'),
      autocommit = True)

  cursor = db_conn.cursor()

  return cursor
