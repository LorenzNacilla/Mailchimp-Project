import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from mailchimp_marketing import Client

# making a directory for the logs
log_dir = "extract_logs"
os.makedirs(log_dir, exist_ok=True)

# log filename for when the script is run
log_filename = os.path.join(log_dir, f"amplitude_extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# configuration of the logs
logging.basicConfig(
    filemode = "a", # append the data when script is run and not overwrite
    level=logging.INFO, # record any message that is INFO, WARNING, ERROR, or CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename
)

# variable for writing out logs
logger = logging.getLogger()

# loading the environment that contains our API Keys
load_dotenv()

# setting and calling variables from our environment that houses the API keys
api_key = os.getenv('MAILCHIMP_API_KEY')
server_prefix = os.getenv('MAILCHIMP_SERVER_PREFIX')

# setting a start date for our events data can go back x amoubnt of days starting midnight
days_back = 1
start_date = datetime.now() - timedelta(days = days_back)
start_date = start_date.strftime('%Y%m%dT00')

# setting an end date for our events data i.e. today
end_date = datetime.now()
end_date = end_date.strftime('%Y%m%dT23')

mailchimp = Client()
mailchimp.set_config({
  "api_key": api_key,
  "server": server_prefix
})

response = mailchimp.ping.get()
print(response)