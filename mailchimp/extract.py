import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from mailchimp_marketing import Client

load_dotenv()

api_key = os.getenv('MAILCHIMP_API_KEY')
server_prefix = os.getenv('MAILCHIMP_SERVER_PREFIX')

mailchimp = Client()
mailchimp.set_config({
  "api_key": api_key,
  "server": server_prefix
})

response = mailchimp.ping.get()
print(response)