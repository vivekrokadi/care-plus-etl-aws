
import boto3
import pandas as pd
from io import StringIO
import pyarrow as pa
import pyarrow.parquet as pq
import io
from urllib.parse import unquote_plus


def save_parquet_to_s3(df, bucket, key):
    table = pa.Table.from_pandas(df, preserve_index=False)

    parquet_buffer = io.BytesIO()
    pq.write_table(table, parquet_buffer)

    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=parquet_buffer.getvalue()
    )

    print(f"Parquet saved to s3://{bucket}/{key}")


def read_ticket_from_s3(bucket, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)

    csv_content = response['Body'].read().decode('utf-8')

    return csv_content


def lambda_handler(event, context):

    record = event['Records'][0]

    bucket_name = record['s3']['bucket']['name']
    input_key = unquote_plus(record['s3']['object']['key'])

    print(f"Triggered by: s3://{bucket_name}/{input_key}")

    csv_content = read_ticket_from_s3(bucket_name, input_key)

    if not csv_content.strip():
        print("CSV file is empty.")
        return

    df = pd.read_csv(StringIO(csv_content))

    print(f"Original shape: {df.shape}")

    df = df.dropna(subset=['ticket_id'])

    df = df.dropna(axis=1, how='all')

    fix_priority = {
        'Lw': 'Low',
        'Hgh': 'High',
        'Medum': 'Medium'
    }

    if 'priority' in df.columns:
        df['priority'] = df['priority'].replace(fix_priority)

    if 'num_interactions' in df.columns:
        df = df[df['num_interactions'] >= 0]

    if 'created_at' in df.columns:
        df['created_at'] = pd.to_datetime(
            df['created_at'], errors='coerce'
        )

    if 'resolved_at' in df.columns:
        df['resolved_at'] = pd.to_datetime(
            df['resolved_at'], errors='coerce'
        )

    df = df.drop_duplicates()

    print(df.shape)
    print(df.head())

    output_file_name = input_key.split('/')[-1].replace(
        '.csv', '.parquet'
    )

    output_key = f'support-tickets/processed/{output_file_name}'

    save_parquet_to_s3(df, bucket_name, output_key)

    print("Ticket processing completed successfully!")
