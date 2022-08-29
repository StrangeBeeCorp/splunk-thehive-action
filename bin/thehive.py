# encoding = utf-8

# TODO:
# - improve logging
# - see if organisation is required/necessary
# - add input controls

import requests
import sys
import os
import tempfile
import json 
import logging
from logging import handlers


def setup_logger(level):
  logger = logging.getLogger("thehive_alert_logger")
  logger.propagate = False
  logger.setLevel(level)
  file_handler = handlers.RotatingFileHandler(os.environ['SPLUNK_HOME'] + '/var/log/splunk/thehive_alerts.log', maxBytes=1000000, backupCount=3)
  formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
  file_handler.setFormatter(formatter)
  logger.addHandler(file_handler)
  return logger



def _verify_ssl_certificate(disablessl: int) -> bool:
  if disablessl == '0':
    return True
  else:
    return False

def _sanitize_thehive_url(thehive_url: str) -> str:
    """Sanitize the base url for the client."""
    if thehive_url.endswith("/"):
        return thehive_url[:-1]
    return thehive_url


def run(inputdata): 
  ## Read configuration
  configuration = inputdata.get('configuration')
  result = inputdata.get('result')

  url = configuration.get('thehiveurl')
  apikey = configuration.get('thehiveapikey')
  endpoint = configuration.get('thehiveendpoint')
  proxyurl = configuration.get('thehiveproxy', '')
  disablessl = configuration.get('disable_ssl_certificate')
  cacert = configuration.get('thehivecustomca', '')
  # organisation = 


  ## prepare request
  headers = dict()
  headers["Authorization"] = f"Bearer {apikey}"
  headers = {**headers, "Content-Type": "application/json"}
  proxies = {
    'http': proxyurl,
    'https': proxyurl
  }
  endpoint_url = f"{_sanitize_thehive_url(url)}/api/v1/function/{endpoint}"
  s = requests.Session()
  s.headers = headers
  s.proxies = proxies
  if cacert == '':
    s.verify = _verify_ssl_certificate(disablessl)
  else:
    f = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    f.write(cacert)
    f.close()
    s.verify = f.name


  response = s.post(endpoint_url, json=result)
  try:
    f
    os.unlink(f.name)
  except NameError:
    pass
  s.close()

def main():
  if len(sys.argv) > 1 and sys.argv[1] == "--execute":
    logger = setup_logger(logging.INFO) # TODO: improve logging
    logger.info("executed") # TODO: remove
    inputdata = json.loads(sys.stdin.read())
    run(inputdata)

  if len(sys.argv) > 1 and sys.argv[1] == "--test":
    inputdata = dict()
    cert = """"""
    inputdata = {
      'configuration': {
        'thehiveurl': '',
        'thehiveapikey': '',
        'disable_ssl_certificate': 0,
        'thehiveproxy': '',
        'thehiveendpoint': '',
        'thehivecustomca': cert
      },
      'result': {
      }
    }
    run(inputdata)

if __name__ == "__main__":
  main()
