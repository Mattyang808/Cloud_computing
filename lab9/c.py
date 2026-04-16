import boto3, io
from PIL import Image

s3 = boto3.client("s3", region_name="ap-south-1")
obj = s3.get_object(Bucket="24181422-lab9", Key="faces.jpg")
raw = obj["Body"].read()

im = Image.open(io.BytesIO(raw))
print(im.format, im.mode, im.size) 