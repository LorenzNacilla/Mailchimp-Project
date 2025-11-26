import json
import requests
import os
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

# assigning variables for directories
log_dir = "extract_logs"

campaign_dir = "campaign_data"
reports_dir = "reports_data"

# making the directories
os.makedirs(log_dir, exist_ok=True)

os.makedirs(campaign_dir, exist_ok=True)
os.makedirs(reports_dir, exist_ok=True)

# log filename for when the script is run
log_filename = os.path.join(log_dir, f"mailchimp_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

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

            logger.info("Campaign data retrieved successfully")
            logger.info(f"There were {len(all_campaigns)} campaigns in the last {days_back} days")
            print("Campaign data retrieved successfully")
            print(f"There were {len(all_campaigns)} campaigns in the last {days_back} days")

            for campaign in all_campaigns:
                c_id = campaign['id']
                c_title = campaign['settings']['title']

                reports = mailchimp.reports.get_campaign_click_details(f"{c_id}")

                logger.info(f"ID: {c_id} | Title: {c_title}")

            campaign_filename = f'{campaign_dir}/mailchimp_campaigns_{timestamp}.json'

            with open(campaign_filename, 'w', encoding='utf-8') as f:
                json.dump(all_campaigns, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully saved {len(all_campaigns)} campaigns to {campaign_filename}")
            print(f"Campaigns saved to: {campaign_filename}")

        except Exception as e:
            print(f"Error fetching campaigns: {e}")

# ---------------------------------------------------------------------------------------------------------------------------------
        # reports data

        # try:
        #     reports = mailchimp.reports.get_all_campaign_reports(
        #         count = 1000,
        #         since_send_time = start_date
        #     )

        #     all_reports = reports['reports']
        #     logger.info("Reports data retrieved successfully")
        #     logger.info(f"There were {len(all_reports)} reports in the last {days_back} days")
        #     print("Reports data retrieved successfully")
        #     print(f"There were {len(all_reports)} reports in the last {days_back} days")

        #     reports_filename = f'{reports_dir}/mailchimp_reports_{timestamp}.json'

        #     with open(reports_filename, 'w', encoding='utf-8') as f:
        #         json.dump(all_reports, f, indent=2, ensure_ascii=False)

        #     logger.info(f"Successfully saved {len(all_reports)} reports to {reports_filename}")
        #     print(f"Reports saved to: {reports_filename}")

        # except Exception as e:
        #    print(f"Error fetching reports: {e}")
    else:
        logger.error(f"API health check failed. Response: {response}")
        print(f"API health check failed. Response: {response}")  
except ApiClientError as e:
    logger.error(f"Failed to connect to Mailchimp API: {e}")
    print(f"Failed to connect to Mailchimp API: {e}")
except Exception as e:
    logger.error(f"Unexpected error during API connection: {e}")
    print(f"Unexpected error during API connection: {e}")