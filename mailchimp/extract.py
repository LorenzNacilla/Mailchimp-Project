import json
import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

# assigning variables for directories
campaign_log_dir = "extract_logs"
reports_log_dir = "reports_logs"

campaign_dir = "campaign_data"
reports_dir = "reports_data"

# making the directories
os.makedirs(campaign_log_dir, exist_ok=True)
os.makedirs(reports_log_dir, exist_ok=True)

os.makedirs(campaign_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)

# log filename for when the script is run
campaign_log_filename = os.path.join(campaign_log_dir, f"mailchimp_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# configuration of the logs
logging.basicConfig(
    filemode = "a", # append the data when script is run and not overwrite
    level=logging.INFO, # record any message that is INFO, WARNING, ERROR, or CRITICAL
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=campaign_log_filename
)

# variable for writing out logs
campaign_logger = logging.getLogger()

# loading the environment that contains our API Keys
load_dotenv()

# setting and calling variables from our environment that houses the API keys
api_key = os.getenv('MAILCHIMP_API_KEY')
server_prefix = os.getenv('MAILCHIMP_SERVER_PREFIX')

# setting a start date for our events data can go back x amoubnt of days starting midnight
days_back = 90
start_date = datetime.now() - timedelta(days = days_back)
start_date = start_date.isoformat()

# timestamp for when the script is run
timestamp = datetime.now().strftime('%Y%m%d')

# mailchimp config
mailchimp = Client()
mailchimp.set_config({
  "api_key": api_key,
  "server": server_prefix
})

try: # check response to mailchimp
    response = mailchimp.ping.get()
    logger.info(f"API Call Response Code: {response}")
    print(response)

    if response == {
    "health_status": "Everything's Chimpy!"
    }:
        # campaign data
        try:
            campaigns = mailchimp.campaigns.list(
                count = 1000,
                status = "sent",
                since_send_time = start_date,
                sort_field = "send_time",
                sort_dir="DESC"
            )

            all_campaigns = campaigns['campaigns']
            campaign_logger.info("Campaign data retrieved successfully")
            campaign_logger.info(f"There were {len(all_campaigns)} campaigns in the last {days_back} days")
            print("Data retrieved successfully")
            print(f"There were {len(all_campaigns)} campaigns in the last {days_back} days")

            filename = f'{campaign_dir}/mailchimp_campaigns_{timestamp}.json'

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(all_campaigns, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully saved {len(all_campaigns)} campaigns to {filename}")
            print(f"Campaigns saved to: {filename}")

        except Exception as e:
            print(f"Error fetching campaigns: {e}")

        try:
            reports = mailchimp.reports(
                count = 1000,
                since_send_time = start_date
            )


    else:
        logger.error(f"API health check failed. Response: {response}")
        print(f"API health check failed. Response: {response}")  
except ApiClientError as e:
    logger.error(f"Failed to connect to Mailchimp API: {e}")
    print(f"Failed to connect to Mailchimp API: {e}")
except Exception as e:
    logger.error(f"Unexpected error during API connection: {e}")
    print(f"Unexpected error during API connection: {e}")