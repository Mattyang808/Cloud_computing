import boto3


REGION = "ap-south-1"
ALIAS  = "alias/24181422" 


kms = boto3.client("kms", region_name=REGION)

resp = kms.create_key(
    Description="CITS5503 lab4 CMK",
    KeyUsage="ENCRYPT_DECRYPT",
    KeySpec="SYMMETRIC_DEFAULT",
    Origin="AWS_KMS"
)
key_id = resp["KeyMetadata"]["KeyId"]
print("KeyId:", key_id)

# create alias
kms.create_alias(AliasName=ALIAS, TargetKeyId=key_id)
print("Alias created:", ALIAS)