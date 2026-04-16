import boto3

REGION = "ap-south-1"
TABLE = "CloudFiles"

# local source
local = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")
src = local.Table(TABLE)

# aws destination
aws = boto3.resource("dynamodb", region_name=REGION)
dst = aws.Table(TABLE)

# minimal scan + batch_write (no pagination/edge cases for lab)
items = src.scan().get("Items", [])
with dst.batch_writer() as bw:
    for it in items:
        bw.put_item(Item=it)
print(f"Copied {len(items)} items from local → AWS.")