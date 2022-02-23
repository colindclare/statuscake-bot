#!/usr/bin/env python
'''Bootstrap DB for StatusCake Bot'''
import sys
import os
import MySQLdb

# Global vars
DB_CREDS = {
  'host': os.environ.get('DB_HOST'),
  'user': os.environ.get('DB_USER'),
  'pass': os.environ.get('DB_PASS'),
  'port': os.environ.get('DB_PORT'),
  'name': os.environ.get('DB_NAME'),
}

def bootstrap_db(cur, db_name):

  cur.execute('''CREATE TABLE IF NOT EXISTS paused_tests (
    `id` int(10) unsigned NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `test_id` int(10) unsigned NOT NULL,
    `domain_name` varchar(255) NOT NULL,
    `pause_start` int(10) NOT NULL,
    `pause_end` int(10) NOT NULL,
    `pause_user` varchar(255) NOT NULL),
    `unpaused_by` varchar(255) NOT NULL)'''
  )

def main():
  try:
    connection = MySQLdb.connect(
      host = DB_CREDS['host'],
      user = DB_CREDS['user'],
      password = DB_CREDS['pass'],
      port = int(DB_CREDS['port']),
  )
  except mariadb.Error as e:
    print(f'Error connecting to the database: {e}')
    sys.exit(1)

  cursor = connection.cursor()

  try:
    bootstrap_db(cursor, DB_CREDS['name'])
  except mariadb.Error as e:
    print(f'Error creating database/table: {e}')
    connection.close()
    sys.exit(1)

if __name__ == '__main__':
  main()
