#!/usr/bin/env python
'''StatusCake Bot - a Slack bot to pause or resume StatusCake tests.'''
import json
import os
import requests
import threading
import time
import validators
from config import Config
from helpers import Helpers
import scdb
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Pull in messages
with open(os.path.dirname(__file__) + '/blocks.json', encoding='utf-8') as msgs:
  MESSAGES = json.load(msgs)

# Initializes app with bot token and socket mode handler
app = App(
  token=Config.get_bot_token(),
  signing_secret=Config.get_sign_secret())


@app.command(Config.get_command())
def statuscake_response(ack, respond, say, command):
  ack()
  arg_list = command['text'].split()
  args = {
    'action' :  arg_list[0],
    'domain_name' : '' if len(arg_list) < 2 else arg_list[1],
    'interval' : '1h' if len(arg_list) < 3 else arg_list[2],
  }

  if validate_args(args, respond):
    sc_tests = requests.get(
      Config.API_URL,
      headers=Config.AUTH_HEADERS,
      params=Config.TEST_PARAMS).json()

    paused_domains = []

    if args['action'] == 'list':
      for test in sc_tests['data']:
        test_domain = [x.strip() for x in test['name'].split('|')]
        if test['paused']:
          paused_domains.append(test_domain[1])
      say('Paused tests:\n' + '\n'.join(paused_domains))
    else:
      for test in sc_tests['data']:
        test_domain = [x.strip() for x in test['name'].split('|')]
        if args['domain_name'] in test_domain:
          pause_url = Config.API_URL + '/' + str(test['id'])
          if args['action'] == 'pause' and test['paused']:
            respond(f'Test for domain {args["domain_name"]} is already paused')
            return False
          else:
            modify_test(pause_url, args, say, command)
            db_info = set_test_db_info(test, args, command)
            if args['action'] == 'pause':
              scdb.add_pause(bot_cur, db_info)
            elif args['action'] == 'resume':
              scdb.set_unpause(bot_cur, db_info)

        elif args['domain_name'] in test_domain[1]:
          # Checks if test was configured with a subdomain
          respond(f'''Domain {args["domain_name"]} not found. \
Found similar subdomain: {test_domain[1]}''')


def validate_args(args, respond):
  if args['action'] == 'help':
    respond(text='Help message',
      blocks=MESSAGES['help_message']['blocks'])
    return False

  if args['action'] not in Config.ALLOWED_ACTIONS:
    respond(f'Invalid action: {args["action"]}. Must be one of: pause, resume')
    return False

  if not validators.domain(args['domain_name']) and args['action'] != 'list':
    respond(f'Improperly formatted domain name: {args["domain_name"]}.')
    return False

  if args['interval'][-1] not in Config.TIME_CONVERSION:
    respond(f'''Invalid interval: {args["interval"]}. \
                Must be formatted as <number>[m|h|d|s|w].''')
    return False

  return True


def convert_to_seconds(interval):
  return int(interval[:-1]) * Config.TIME_CONVERSION[interval[-1]]


def modify_test(url, args, say, command):
  if args['action'] == 'pause':
    pause_bool = 'true'
    pause_msg = 'Test for {0} paused for {2} by <@{1}>.'
  elif args['action'] == 'resume':
    pause_bool = 'false'
    pause_msg = 'Test for {0} resumed by <@{1}>.'

  pause_params = {'paused': pause_bool}
  Helpers.request_put(url, Config.AUTH_HEADERS, pause_params)

  say(pause_msg.format(
    args['domain_name'],
    command['user_name'],
    args['interval'])
  )


def set_test_db_info(test_params, args, command):
  start_time = int(time.time())
  interval = convert_to_seconds(args['interval'])
  end_time = start_time + interval

  if args['action'] == 'resume':
    unpause_user = command['user_name']
    status = 'unpaused'
  else:
    unpause_user = 'None'
    status = 'paused'

  test_info = {}
  test_info['test_id'] = test_params['id']
  test_info['domain_name'] = test_params['name'].split('|')[1].strip()
  test_info['pause_start'] = start_time
  test_info['pause_end'] = end_time
  test_info['status'] = status
  test_info['paused_by'] = command['user_name']
  test_info['unpaused_by'] = unpause_user

  return test_info

# Start your app
if __name__ == '__main__':

  # Create MariaDB cursor
  bot_cur = scdb.get_cursor()
  clean_cur = scdb.get_cursor()

  # Start cleanup thread
  cleanup = threading.Thread(target=scdb.clean_exp_pauses, args=(clean_cur,))
  cleanup.start()

  SocketModeHandler(app, Config.get_app_token()).start()
