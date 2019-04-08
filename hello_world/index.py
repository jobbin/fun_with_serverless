# -*- coding: utf-8 -*-
import logging

def handler(event, context):
  logger = logging.getLogger()
  logger.info(event)
  status = '200 OK'
  response_headers = [('Content-type', 'text/plain')]
  context(status, response_headers)
  return [b'Hello world!\n']
