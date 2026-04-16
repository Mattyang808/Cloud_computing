import boto3, botocore, os, sys

REGION = "ap-south-1"
BUCKET = "24181422-lab9"

s3 = boto3.client("s3", region_name=REGION)

# Create the bucket in ap-south-1 (no special-case logic)
try:
    s3.create_bucket(
        Bucket=BUCKET,
        CreateBucketConfiguration={"LocationConstraint": REGION}
    )
except botocore.exceptions.ClientError as e:
    if e.response.get("Error", {}).get("Code") != "BucketAlreadyOwnedByYou":
        raise

# Upload the four files
files = ["urban.jpg", "beach.jpg", "faces.jpg", "text.jpg"]
missing = [f for f in files if not os.path.exists(f)]
if missing:
    print("Missing:", *missing); sys.exit(1)

for f in files:
    s3.upload_file(f, BUCKET, f)

print("Done.")


