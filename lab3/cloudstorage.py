import os
import boto3
import base64


ROOT_DIR = '.'
ROOT_S3_DIR = '24181422-cloudstorage'


s3 = boto3.client("s3")

bucket_config = {'LocationConstraint': 'ap-south-1'} 

def upload_file(folder_name, file, file_name):
    print("Uploading %s" % file)
    # Upload file to S3 bucket
    s3_key = folder_name + file_name if folder_name else file_name
    s3.upload_file(file, ROOT_S3_DIR, s3_key)


# Main program
# Insert code to create bucket if not there

try:
    response = s3.create_bucket(
        Bucket=ROOT_S3_DIR,
        CreateBucketConfiguration=bucket_config
    )
    print(response)
except Exception as error:
    print("Bucket creation error:",error)
    pass


# parse directory and upload files

for dir_name, subdir_list, file_list in os.walk(ROOT_DIR, topdown=True):
    if dir_name != ROOT_DIR:
        for fname in file_list:
            upload_file("%s/" % dir_name[2:], "%s/%s" % (dir_name, fname), fname)


print("done")
