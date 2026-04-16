import json, boto3

bucket = "24181422-cloudstorage"
student_email = "24181422@student.uwa.edu.au"

policy = {
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "AllowAllS3ActionsInUserFolderForUserOnly",
    "Effect": "Deny",
    "Principal": "*",
    "Action": "s3:*",
    "Resource": f"arn:aws:s3:::{bucket}/*",
    "Condition": {"StringNotLike": {"aws:username": student_email}}
  }]
}

s3 = boto3.client("s3")
s3.put_bucket_policy(Bucket=bucket, Policy=json.dumps(policy))
print("Applied policy to", bucket)