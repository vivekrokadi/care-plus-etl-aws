import os
import boto3
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

S3_BUCKET = "care-plus-data-lake"
S3_PREFIX = "support-logs/raw/"
DATE_TRACKER_FILE = "../../log_date_tracker.txt"
LOGS_FOLDER = "../../raw_data/day-wise-logs-data/"

AWS_CONFIG = {
    "aws_access_key_id" : os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key" : os.getenv("AWS_SECRET_ACCESS_KEY"),
    "region_name" : os.getenv("AWS_REGION")
}

def get_absolute_path(relative_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

def read_last_date(file_path):
    abs_path = get_absolute_path(file_path)
    if os.path.exists(abs_path):
        with open(abs_path, 'r') as file:
            return file.read().strip()
    return "2025-06-30"

def update_last_date(file_path, new_date):
    abs_path = get_absolute_path(file_path)
    with open(abs_path, 'w') as file:
        file.write(new_date)

def get_next_date(last_date_str):
    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
    next_date = last_date + timedelta(days=1)
    return next_date.strftime("%Y-%m-%d")

def upload_log_file_to_s3(file_path, bucket, key):
    s3 = boto3.client('s3', **AWS_CONFIG)
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    s3.put_object(Bucket=bucket, Key=key, Body=content)
    print(f"Uploaded log file to s3://{bucket}/{key}")


def run_log_ingestion():
    last_date = read_last_date(DATE_TRACKER_FILE)
    next_date = get_next_date(last_date)
    print(f"Starting log ingestion for date: {next_date}")

    file_name = f"support_logs_{next_date}.log"
    log_file_full_path = get_absolute_path(os.path.join(LOGS_FOLDER, file_name))

    if not os.path.exists(log_file_full_path):
        print(f"Log file not found: {log_file_full_path} Skipping Upload.")
        return

    s3_key = f"{S3_PREFIX}{file_name}"
    upload_log_file_to_s3(log_file_full_path, S3_BUCKET, s3_key)

    update_last_date(DATE_TRACKER_FILE, next_date)
    print(f"Updated tracker to {next_date}\n")


if __name__ == "__main__":
    run_log_ingestion()

