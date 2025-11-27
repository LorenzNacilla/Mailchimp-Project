import json
import requests
import os
import logging
import time
from dotenv import load_dotenv
from datetime import datetime, timedelta
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError

# assigning variables for directories
log_dir = "extract_logs"

campaign_dir = "campaign_data"
click_reports_dir = "click_reports_data"

# making the directories
os.makedirs(log_dir, exist_ok=True)

os.makedirs(campaign_dir, exist_ok=True)
os.makedirs(click_reports_dir, exist_ok=True)

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
days_back = 120
start_date = datetime.now() - timedelta(days = days_back)
start_date = start_date.isoformat()

# timestamp for when the script is run
timestamp = datetime.now().strftime('%Y%m%d') #_%H%M%S

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
            print(f"Fetching campaigns for the last {days_back} days...")
            logger.info(f"Fetching campaigns for the last {days_back} days...")
            campaigns = mailchimp.campaigns.list(
                count = 1000,
                status = "sent",
                since_send_time = start_date,
                sort_field = "send_time",
                sort_dir="DESC"
            )

            all_campaigns = campaigns['campaigns'] # 

            logger.info("Campaign data retrieved successfully")
            logger.info(f"There were {len(all_campaigns)} campaigns in the last {days_back} days")
            print("Campaign data retrieved successfully")
            print(f"There were {len(all_campaigns)} campaigns in the last {days_back} days")

            for campaign in all_campaigns: # loop through the campaigns for id and title
                c_id = campaign['id']
                c_title = campaign['settings']['title']

                logger.info(f"ID: {c_id} | Title: {c_title}")

            campaign_filename = f'{campaign_dir}/mailchimp_campaigns_{timestamp}.json'

            with open(campaign_filename, 'w', encoding='utf-8') as f:
                json.dump(all_campaigns, f, indent=2, ensure_ascii=False)

            logger.info(f"Successfully saved {len(all_campaigns)} campaigns to {campaign_filename}")
            print(f"Campaigns saved to: {campaign_filename}")

# ------------------------------------------------------------------------------------------------------------------------------
            # click details
            print(f"Getting click details for {len(all_campaigns)} campaigns in the last {days_back} days...")

            all_clicks_data = []

            for i, campaign in enumerate(all_campaigns):
                c_id = campaign['id']

                try:
                    click_report = mailchimp.reports.get_campaign_click_details(c_id, count=1000)

                    click_details = click_report.get('urls_clicked', [])

                    if click_details:
                        all_clicks_data.extend(click_details)

                    time.sleep(0.2)
                
                except Exception as e:
                    logger.warning(f"Error processing {c_id}: {e}")
                    continue

                click_reports_filename = f"{click_reports_dir}/mailchimp_click_reports_{timestamp}.json"

                with open(click_reports_filename, 'w', encoding='utf-8') as f:
                    json.dump(all_clicks_data, f, indent=2, ensure_ascii=False)

                logger.info(f"Successfully saved {len(all_clicks_data)} click details")
                print(f"Click details saved to {click_reports_filename}")

        except Exception as e:
            print(f"Error in processing loop: {e}")
            logger.error(f"Error in processing loop: {e}")

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