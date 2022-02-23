#!/usr/bin/env python3
'''Helper functions for the StatusCake bot'''
import requests

class Helpers:
  @staticmethod
  def request_put(url, headers, params):
    requests.put(
      url,
      headers=headers,
      params=params)
