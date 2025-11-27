import os
import boto3
import logging
from dotenv import load_dotenv
from datetime import datetime

# load environment for our load aws access key, secret key, and bucket name
load_dotenv()

# referencing variables from the .load_env file
aws_access_key = os.getenv("AWS_ACCESS_KEY")
aws_secret_key = os.getenv("AWS_SECRET_KEY")
bucket_name = os.getenv("AWS_BUCKET")

# directories that contain data
campaign_dir = 'campaign_data'

# directory variables for logs and making them
logs_dir = "s3_upload_logs"

os.makedirs(logs_dir, exist_ok = True)

# timestamp variable
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') #_%H%M%S

# log configuration
log_filename = os.path.join(logs_dir, f"mailchimp_s3_upload_{timestamp}.log")
logging.basicConfig(
    filemode = "a",
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_filename
)
logger = logging.getLogger()

# Create an S3 Client using AWS Credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id = aws_access_key,
    aws_secret_access_key = aws_secret_key
)

# ----------------------------------------------------------------------------------------------
# s3 load function

# Directory name: s3 bucket folder name
upload_mapping = {
    "campaign_data": "campaigns",
    "click_reports_data": "click-reports",
    "members_details_data": "members"
}

def upload_directory(local_dir, s3_folder):
    """
    Go through the data directories and upload them to their respective s3 folder. Also deletes from local machine.
    """

    logger.info(f"Checking directory: {local_dir}")
    print(f"Checking directory: {local_dir}")

    # directory check
    if not os.path.exists(local_dir):
        logger.warning(f"Directory not found: {local_dir}. Skipping.")
        print(f"Directory not found: {local_dir}")
        return
    
    # find json files in the directory to upload
    files_to_upload = [f for f in os.listdir(local_dir) if f.endswith(".json")]

    if not files_to_upload:
        logger.info(f"No .json files within {local_dir}")
        print(f"No files in {local_dir}")
        return
    
    logger.info(f"Found {len(files_to_upload)} files to upload from {local_dir}")
    print(f"Found {len(files_to_upload)} files in {local_dir}")

    # Upload
    for filename in files_to_upload:
        local_file_path = os.path.join(local_dir, filename)

        aws_file_destination = f"{s3_folder}/{filename}"

        try:
            s3_client.upload_file(
                local_file_path
                , bucket_name
                , aws_file_destination
            )
            logger.info(f"Uploaded: {filename} to s3://{bucket_name}/{aws_file_destination}")
            print(f"Uploaded: {filename}")

            os.remove(local_file_path)
            logger.info(f"Deleted local file: {local_file_path}")

        except Exception as e:
            logger.error(f"Failed to upload {filename}: {e}")
            print(f"Failed to upload {filename}: {e}")

# ----------------------------------------------------------------------------------------------
# function execution

if __name__ == "__main__":
    logger.info("Starting s3 upload for data directories...")
    print("Starting s3 upload for data directories...")

    for local_folder, s3_target_folder in upload_mapping.items():
        upload_directory(local_folder, s3_target_folder)

    logger.info("s3 upload process finished")
    print("s3 upload process finished")

# # go through my campaign directory for an json data files
# files_to_upload = []
# try:
#     all_campaign_data_files = os.listdir(campaign_dir)
#     for f in all_campaign_data_files:
#         if f.endswith(".json"):
#             files_to_upload.append(f)
# except Exception as e:
#     logger.error(f"Could not read {campaign_dir} directory: {e}")

# if not files_to_upload:
#     logger.info("No new .json files to upload")
# else:
#     if len(files_to_upload) == 1:
#         logger.info("There is 1 json file to upload")
#     else:
#         logger.info(f"There are {len(files_to_upload)} json files to upload")
    
#     for filename in files_to_upload: # go through any new .json files
#         local_file_path = os.path.join(campaign_dir, filename) # full local file path to be read
#         #### archive_file_path = os.path.join(archive_dir, filename) # archive file path

#         # s3filename = f"raw_data/amplitude/{filename}"
#         aws_file_destination = "campaigns/" + filename

#         try:
#             s3_client.upload_file(
#                 local_file_path
#                 , bucket_name
#                 , aws_file_destination
#             )
#             logger.info(f"Uploaded {local_file_path} to s3://{bucket_name}/{aws_file_destination}")

#             os.remove(local_file_path)
#             logger.info(f"Removed file: {local_file_path}")

#         except Exception as e:
#             logger.error(f"Failed during upload/removal for {local_file_path}: {e}")

#     logger.info("s3 upload finished.")
#     print("s3 upload finished.")