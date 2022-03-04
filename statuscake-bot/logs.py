#!/usr/bin/env python3
"""Logger class for easy message output"""
import logging
import sys


class ScbotLogger:
  """Class that wraps logging.Logger"""
  def __init__(self, logger_name):
    self.log_format = '%(asctime)s %(name)s:%(levelname)s - %(message)s'
    logging.basicConfig(stream=sys.stdout,
                        format=self.log_format,
                        level=logging.INFO)
    self.logger = logging.getLogger(logger_name)

  def info(self, message, source=''):
    self.logger.info(source + ' - ' + message)

  def warning(self, message, source=''):
    self.logger.warning(source + ' - ' + message)

  def error(self, message, source=''):
    self.logger.error(source + ' - ' + message)

  def critical(self, message, source=''):
    self.logger.critical(source + ' - ' + message)
