import boto3
import pandas as pd
import logging
from src.logger import logging
from io import StringIO

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

class s3_operations:
    def __init__(self, bucket_name, aws_access_key, aws_secret_key, region_name="us-east-1"):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )
        logging.info("Data Ingestion from S3 bucket initialized")

    def fetch_file_from_s3(self, file_key):
        try:
            logging.info(f"Fetching file '{file_key}' from S3 bucket '{self.bucket_name}'...")
            obj = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            df = pd.read_csv(StringIO(obj['Body'].read().decode('utf-8')))
            logging.info(f"Successfully fetched and loaded '{file_key}' from S3 that has {len(df)} records.")
            return df
        except Exception as e:
            logging.exception(f'Failed to fetch {file_key} from S3: {e}')
            return None

# Example usage
if __name__ == "__main__":
    BUCKET_NAME = "------------------"
    AWS_ACCESS_KEY = "----------------"
    AWS_SECRET_KEY = "------------------"
    FILE_KEY = "---------------"

    data_ingestion = s3_operations(BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY)
    df = data_ingestion.fetch_file_from_s3(FILE_KEY)

    if df is not None:
        print(f"Data fetched with {len(df)} records..")
