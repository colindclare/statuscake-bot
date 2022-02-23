#!/usr/bin/env python3
import requests

class Helpers:
  def request_put(url, headers, params):
    requests.put(
      url,
      headers=headers,
      params=params)