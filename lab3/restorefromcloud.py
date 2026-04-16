import os
import boto3

ROOT_S3_DIR = '24181422-cloudstorage'
RESTORE_DIR = 'restored'

s3 = boto3.client("s3")

def download_file(s3_key, local_path):
    print(f"Downloading {s3_key} to {local_path}")
    # Create directory if it doesn't exist
    local_dir = os.path.dirname(local_path)
    if local_dir and not os.path.exists(local_dir):
        os.makedirs(local_dir)
    
    # Download file from S3
    s3.download_file(ROOT_S3_DIR, s3_key, local_path)


# Create restore directory if it doesn't exist
if not os.path.exists(RESTORE_DIR):
    os.makedirs(RESTORE_DIR)

try:
    # List all objects in the S3 bucket
    response = s3.list_objects_v2(Bucket=ROOT_S3_DIR)
    
    if 'Contents' in response:
        for obj in response['Contents']:
            s3_key = obj['Key']
            
            # Create local file path
            local_path = os.path.join(RESTORE_DIR, s3_key)
            
            # Download the file
            download_file(s3_key, local_path)
    else:
        print("No objects found in bucket")

except Exception as error:
    print(f"Error restoring from S3: {error}")

print("Restore completed")