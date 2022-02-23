#!/usr/bin/env python3
import os

class Config:
  API_URL = 'https://api.statuscake.com/v1/uptime'

  API_TOKEN = os.environ.get('SC_TOKEN')
  AUTH_HEADERS = {'Authorization': 'Bearer ' + API_TOKEN}

  APP_TOKEN = os.environ.get('SLACK_APP_TOKEN')
  BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
  SIGN_SECRET = os.environ.get('SLACK_SIGN_SECRET')

  ALLOWED_ACTIONS = ['pause', 'resume', 'list']

  TEST_PARAMS = {
      'tags': 'ESG,MAPPS',
      'matchany': 'true',
      'limit': '100'
  }
  TIME_CONVERSION = {
      's': 1,
      'm': 60,
      'h': 3600,
      'd': 86400,
      'w': 604800
  }

  @staticmethod
  def get_app_token():
    return Config.APP_TOKEN

  @staticmethod
  def get_command():
    env = os.environ.get('SCBOT_ENV')
    return '/scbotdev' if env == 'dev' else '/statuscake'

  @staticmethod
  def get_bot_token():
    return Config.BOT_TOKEN

  @staticmethod
  def get_sign_secret():
    return Config.SIGN_SECRET

