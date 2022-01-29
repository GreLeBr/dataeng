import os
import logging

from datetime import datetime

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from google.cloud import storage
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator
import pyarrow.csv as pv
import pyarrow.parquet as pq

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BUCKET = os.environ.get("GCP_GCS_BUCKET")

dataset_file = 'fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
dataset_url = f"https://nyc-tlc.s3.amazonaws.com/trip+data/{dataset_file}"
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")
parquet_file = dataset_file.replace('.csv', '.parquet')
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')



# url_list=[]
# for u in range(19,21):
#   for x in ["%.2d" % i for i in range(1, 13)]:
#     url_list.append(f"https://s3.amazonaws.com/nyc-tlc/trip+data/fhv_tripdata_20{u}-{x}.csv")
# https://nyc-tlc.s3.amazonaws.com/trip+data/fhv_tripdata_2019-01.csv


# URL_PREFIX = 'https://s3.amazonaws.com/nyc-tlc/trip+data' 
# URL_TEMPLATE = URL_PREFIX + '/fhv_tripdata_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
# OUTPUT_FILE_TEMPLATE = AIRFLOW_HOME + '/output_{{ execution_date.strftime(\'%Y-%m\') }}.csv'
# TABLE_NAME_TEMPLATE = 'fhv_taxi_{{ execution_date.strftime(\'%Y_%m\') }}'



def format_to_parquet(src_file):
    if not src_file.endswith('.csv'):
        logging.error("Can only accept source files in CSV format, for the moment")
        return
    table = pv.read_csv(src_file)
    pq.write_table(table, src_file.replace('.csv', '.parquet'))


# NOTE: takes 20 mins, at an upload speed of 800kbps. Faster if your internet has a better upload speed
def upload_to_gcs(bucket, object_name, local_file):
    """
    Ref: https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python
    :param bucket: GCS bucket name
    :param object_name: target path & file-name
    :param local_file: source path & file-name
    :return:
    """
    # WORKAROUND to prevent timeout for files > 6 MB on 800 kbps upload speed.
    # (Ref: https://github.com/googleapis/python-storage/issues/74)
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 5 MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024  # 5 MB
    # End of Workaround

    client = storage.Client()
    bucket = client.bucket(bucket)

    blob = bucket.blob(object_name)
    blob.upload_from_filename(local_file)


default_args = {
    "owner": "airflow",
    "start_date": days_ago(380*3),
    "end_date": "2021-12-01",
    "depends_on_past": True,
    "retries": 1,
}



# NOTE: DAG declaration - using a Context Manager (an implicit way)
with DAG(
    dag_id="data_ingestion_fhv",
    schedule_interval="0 6 2 * *", 
    default_args=default_args,
    catchup=True,
    max_active_runs=1,
    tags=['dtc-de'],
) as dag:
    # for dataset_url in url_list:
    #     dataset_file= dataset_url.split("/")[-1]
    #     parquet_file = dataset_file.replace('.csv', '.parquet')
    download_dataset_task = BashOperator(
        task_id="download_dataset_task", # +dataset_url.split("/")[-1].split(".")[0].split("_")[-1],
        bash_command=f"curl -sS {dataset_url} > {path_to_local_home}/{dataset_file}"
    )

    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task", #+dataset_url.split("/")[-1].split(".")[0].split("_")[-1],
        python_callable=format_to_parquet,
        op_kwargs={
            "src_file": f"{path_to_local_home}/{dataset_file}",
        },
    )

    # destroy_csv = BashOperator(
    #     task_id="destroy_csv"+dataset_url.split("/")[-1].split(".")[0].split("_")[-1],
    #     bash_command=f"rm {path_to_local_home}/{dataset_file}"
    # )

    # TODO: Homework - research and try XCOM to communicate output values between 2 tasks/operators
    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task", #+dataset_url.split("/")[-1].split(".")[0].split("_")[-1],
        python_callable=upload_to_gcs,
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{parquet_file}",
            "local_file": f"{path_to_local_home}/{parquet_file}",
        },
    )

    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task", #+dataset_url.split("/")[-1].split(".")[0].split("_")[-1],
        table_resource={
            "tableReference": {
                "projectId": PROJECT_ID,
                "datasetId": BIGQUERY_DATASET,
                "tableId": "external_table_fhv_{{ execution_date.strftime(\'%Y-%m\') }}",
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",
                "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],
            },
        },
    )

    
    download_dataset_task >> format_to_parquet_task >>  local_to_gcs_task >> bigquery_external_table_task
    # download_dataset_task >> format_to_parquet_task >> destroy_csv >> local_to_gcs_task >> bigquery_external_table_task
