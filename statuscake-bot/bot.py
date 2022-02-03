#!/usr/bin/env python
'''StatusCake Bot - a Slack bot to pause or resume StatusCake tests.'''
import json
import os
import requests
import threading
import time
import validators
import scdb
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Global variables
API_URL = 'https://api.statuscake.com/v1/uptime'
API_TOKEN = os.environ.get('SC_TOKEN')
AUTH_HEADERS = {'Authorization': 'Bearer ' + API_TOKEN}
ALLOWED_ACTIONS = ['pause', 'resume', 'list']
ENVIRONMENT = os.environ.get('SCBOT_ENV')
SC_COMMAND = '/scbotdev' if ENVIRONMENT == 'dev' else '/statuscake'

TEST_PARAMS = {
    'tags' : 'ESG,MAPPS',
    'matchany' : 'true',
    'limit' : '100'
}
TIME_CONVERSION = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'w': 604800
}

# Pull in messages
with open(os.path.dirname(__file__) + '/blocks.json', encoding='utf-8') as msgs:
  MESSAGES = json.load(msgs)

# Initializes app with bot token and socket mode handler
app = App(
  token=os.environ.get('SLACK_BOT_TOKEN'),
  signing_secret=os.environ.get('SLACK_SIGN_SECRET'))


@app.command(SC_COMMAND)
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
      API_URL,
      headers=AUTH_HEADERS,
      params=TEST_PARAMS).json()

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
          pause_url = API_URL + '/' + str(test['id'])

          modify_test(pause_url, args, say, command)

          test_info = set_test_info(test, args['interval'], command)

          if args['action'] == 'pause':
            scdb.add_pause(bot_cur, test_info)
          elif args['action'] == 'resume':
            print('scdb.delete_pause(bot_cur, test_info)')

        elif args['domain_name'] in test_domain[1]:
          # Checks if test was configured with a subdomain
          respond(f'''Domain {args["domain_name"]} not found. \
Found similar subdomain: {test_domain[1]}''')


def validate_args(args, respond):
  if args['action'] == 'help':
    respond(text='Help message',
      blocks=MESSAGES['help_message']['blocks'])
    return False

  if args['action'] not in ALLOWED_ACTIONS:
    respond(f'Invalid action: {args["action"]}. Must be one of: pause, resume')
    return False

  if not validators.domain(args['domain_name']) and args['action'] != 'list':
    respond(f'Improperly formatted domain name: {args["domain_name"]}.')

  if args['interval'][-1] not in TIME_CONVERSION:
    respond(f'''Invalid interval: {args["interval"]}. \
                Must be formatted as <number>[m|h|d|s|w].''')
    return False

  return True


def convert_to_seconds(interval):
  return int(interval[:-1]) * TIME_CONVERSION[interval[-1]]


def modify_test(url, args, say, command):
  if args['action'] == 'pause':
    pause_bool = 'true'
    pause_msg = 'Test for {0} paused for {2} by <@{1}>.'
  elif args['action'] == 'resume':
    pause_bool = 'false'
    pause_msg = 'Test for {0} resumed by <@{1}>.'

  requests.put(
    url,
    headers=AUTH_HEADERS,
    params={'paused':pause_bool})

  say(pause_msg.format(
    args['domain_name'],
    command['user_name'],
    args['interval'])
  )


def set_test_info(test_params, interval, command):
  start_time = int(time.time())
  end_time = start_time + convert_to_seconds(interval)

  test_info = []
  test_info.append(test_params['id'])
  test_info.append(test_params['name'].split('|')[1].strip())
  test_info.append(start_time)
  test_info.append(end_time)
  test_info.append(command['user_name'])
  print(test_info)

  return tuple(test_info)

# Start your app
if __name__ == '__main__':

  # Create MariaDB cursor
  bot_cur = scdb.get_cursor()
  clean_cur = scdb.get_cursor()

  # Start cleanup thread
  # cleanup = threading.Thread(target=scdb.clean_pauses, args=(clean_cur,))
  # cleanup.start()

  SocketModeHandler(app, os.environ['SLACK_APP_TOKEN']).start()
